from dotenv import load_dotenv
import httpx
from product_review_crew.crew import ProductReviewCrew
import google.generativeai as genai
import pandas as pd
import os
import requests
import random
import yaml
import time


load_dotenv()


def improve_response(prompt, query):
    try:
        genai.configure(api_key=os.getenv('GENAI_KEY'))
        model = genai.GenerativeModel("gemini-pro")
        result = model.generate_content(prompt + query)
        return result.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Error: {e}")
        return ""


def wp_post(title, result, product):
    print('Start posting to wordpress')
    if len(title) > 100:
        prompt = "Provide a shorter title that is less than 70 characters."
        title = improve_response(prompt, title)
        if title == "":
            return

    improved_text = result  # improve_response(final_prompt, final_text)
    
    if improved_text == "":
        improved_text = result
    # Upload to wordpress
    improved_text.replace('Introduction:', '')

    import requests
    from requests.auth import HTTPBasicAuth

    # Login credentials
    login = os.getenv('wp_login')
    password = os.getenv('wp_password')

    # URL to send the POST request to
    url = os.getenv('wp_url')

    affiliate_url = product['link']
    product_name = product['product']

    prompt = "Provide a very short rephrased version of the call to action, like act now, order now, get it now, etc, that maintains a direct and imperative tone suitable for a marketing context."
    cta_words = improve_response(prompt, "Order Now!")

    # summarize_prompt = "Provide a short summary containing only 10 words or less that highlights the main benefits of the product."
    # meta_desc = improve_response(summarize_prompt, final_text)

    cta_button = f"""
        <p>
        <a href="{affiliate_url}" target="_blank" rel="noopener">{cta_words}. Get Your {product_name}</a>
    """

    improved_text += cta_button

    removed_from_title = [
        'Title: ',
        '*',
        '<h2>',
        '</h2>',
        '<h1>',
        '</h1>',
        '<p>',
        '</p>',
        '<h3>',
        '</h3>',
        '”',
        '"'
    ]
    for remov in removed_from_title:
        title = title.replace(remov, "")

    media_id = product['media_id']
    tag_id = product['tag_id']
    if product['type'] == 'supplement':
        tags = [4, int(tag_id), 5]
    elif product['type'] == 'book':
        tags = [54, int(tag_id), 5]
    elif product['type'] == 'deliverable':
        tags = [148, int(tag_id), 5]

    # Data for creating a new post
    data = {
        "title": title,
        "status": 'draft',  # "publish",
        "content": improved_text,
        "comment_status": "closed",
        "ping_status": "closed",
        "featured_media": int(media_id),
        "tags": tags,
        # "meta": {
        #     "rank_math_title": title,
        #     "rank_math_description": meta_desc,
        #     "rank_math_focus_keyword": product_name
        # }
    }

    # Make the POST request with basic authentication
    response = requests.post(url, auth=HTTPBasicAuth(login, password), json=data)
    return response


def contains_letters(s):
    return any(c.isalpha() for c in s)


def generate_post(inputs):
    result = ProductReviewCrew().crew(
        'article_seed').kickoff(
            inputs=inputs)
    results = result.split("\n")
    print(results)
    judul = results[0]
    counter = 0
    expanded = ''
    # do not explain the last paragraph and last item
    last_h2_index = 0
    for i in range(len(results)-1, -1, -1):
        if "<h2>" in results[i]:
            last_h2_index = i
            break
    if last_h2_index != 0:
        for item in results:
            counter += 1
            if counter < 4:
                expanded += item + '\n'
                continue
            if item == '':
                continue
            if '<h2>' in item:
                expanded += item + '\n'
                continue

            if not contains_letters(item):
                continue

            if counter > (last_h2_index + 1):
                expanded += item + '\n'
                continue
            explanation_input = {
                'item': item
            }
            print('here')
            explanation = ProductReviewCrew().crew(
                'explain').kickoff(
                    inputs=explanation_input)
            expanded += explanation + '\n'
        return judul, expanded
    else:
        return None, None


def generate_post_formatted(inputs):
    expand = False
    while True:
        result = ProductReviewCrew().crew(
            'article_seed').kickoff(
                inputs=inputs)
        results = result.split("\n")
        judul = results[0]
        print(results)
        counter = 0
        expanded = ''
        h2_indices = [
            index for index, element in enumerate(
                results)
            if ('<H2>' in element or '<h2>' in element)]
        # recreate if the document is not formatted with h2
        if len(h2_indices) == 0:
            print('recreate the article')
            continue
        last_h2_index = h2_indices[len(h2_indices)-1]
        for item in results:
            if counter > 1 and counter < 4:
                expanded += item + '\n'
                continue
            counter += 1
            if item == '':
                continue
            if '<H2>' in item:
                expanded += item + '\n'
                continue

            if not contains_letters(item):
                continue

            if counter > (last_h2_index + 1):
                expanded += item + '\n'
                continue
            if expand:
                explanation_input = {
                    'item': item
                }
                explanation = ProductReviewCrew().crew(
                    'explain').kickoff(
                        inputs=explanation_input)
                expanded += explanation + '\n'
            else:
                expanded += item + '\n'
        if expanded:
            break
    return judul, expanded


def product_review_random(num_posts):
    file_name = 'products_all.csv'
    product = pd.read_csv(f"products/{file_name}")
    print(f"Will be creating {num_posts} number of posts")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    yaml_file_path = os.path.join(script_dir, 'config', 'review_details.yaml')
    with open(yaml_file_path, 'r') as file:
        details_dict = yaml.safe_load(file)

    for i in range(0, num_posts):
        try:
            print(f"Preparing post number {i}")
            lowest = product[product['post_count'] == product['post_count'].min()]
            idx_list = lowest.index.to_list()
            idx_rand = random.choice(idx_list) if len(idx_list) > 1 else idx_list[0]
            product_type = product['type'][idx_rand]
            details = details_dict[product_type]['details']  # detail of items to be reviewed
            product_detail = product['product_detail'][idx_rand]
            product_name = product['product'][idx_rand] + f' {product_type}'
            inputs = {
                'item': product_name,
                'topic': product_name,
                'details': details,
                'product_detail': product_detail,
            }
            judul, content = generate_post_formatted(inputs)
            print(content)
            if content:
                response = wp_post(judul, content, product.iloc[idx_rand])
                product.loc[idx_rand, 'post_count'] += 1
                product.to_csv(f'products/{file_name}', index=False)
                time.sleep(30)
        except requests.exceptions.HTTPError as e:
            print(e)
            if response.status_code == 429:
                time.sleep(60)
        except httpx.RemoteProtocolError as e:
            print(e)
            time.sleep(60)
        except requests.exceptions.SSLError as e:
            print(e)
            # retry to post 3 times
            for i in range(3):
                response = wp_post(judul, content, product.iloc[idx_rand])
                if response.status_code == 200:
                    break
                else:
                    time.sleep(60)


def product_review_new():
    product = pd.read_csv("products/products.csv")
    num_posts = product.shape[0]
    print(f"Will be creating {num_posts} number of posts")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    yaml_file_path = os.path.join(script_dir, 'config', 'review_details.yaml')
    with open(yaml_file_path, 'r') as file:
        details_dict = yaml.safe_load(file)

    for i in range(0, num_posts):
        try:
            lowest = product[product['post_count'] == product['post_count'].min()]
            idx_rand = lowest.index.to_list()[0]
            print(f"Preparing post number {i}")
            product_type = product['type'][idx_rand]
            details = details_dict[product_type]['details']
            product_name = product['product'][idx_rand] + f' {product_type}'
            product_detail = product['product_detail'][idx_rand]
            inputs = {
                'item': product_name,
                'topic': product_name,
                'details': details,
                'product_detail': product_detail,
            }
            result = generate_post_formatted(inputs)
            response = wp_post(result, product.iloc[idx_rand])
            product.loc[idx_rand, 'post_count'] += 1
            product.to_csv('products/products.csv', index=False)
        except requests.exceptions.HTTPError as e:
            print(e)
            if response.status_code == 429:
                time.delay(60)


def test():
    inputs = {
        'product': 'LavaSlim',
    }
    result = ProductReviewCrew().crew(
        'test').kickoff(
            inputs=inputs)
    print(result)

    
def randomize_product_count():
    file_name = 'products_all.csv'
    prod = pd.read_csv(f'products/{file_name}')
    for i in range(0, prod.shape[0]):
        prod.loc[i, 'post_count'] = random.randint(1, 5)
    prod.to_csv(f'products/{file_name}', index=False)
    print('Finish randomize post count')


def hightlight_product_strength(product_name):
    inputs = {
        'product': product_name,
    }
    result = ProductReviewCrew().crew(
        'highlight').kickoff(
            inputs=inputs)
    print(result)


def create_ads(topic):
    inputs = {
        'topic': topic,
    }
    result = ProductReviewCrew().crew(
        'create_ads').kickoff(
            inputs=inputs)
    print(result)


def get_ingredients(product_name):
    inputs = {
        'product': product_name,
    }
    result = ProductReviewCrew().crew(
        'get_ingredients').kickoff(
            inputs=inputs)
    print(result)


def run():
    product_name = 'GlucoBerry: Health Supplement for Regulating Blood Sugar'
    topic = 'Regulating blood sugar with herbal supplement'
    create_ads(topic)
    # hightlight_product_strength(product_name)
    # get_ingredients(product_name)
    # randomize_product_count()
    # product_review_new()
    # product_review_random(1)


if __name__ == '--main__':
    run()

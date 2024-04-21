from dotenv import load_dotenv
from product_review_crew.crew import ProductReviewCrew
import google.generativeai as genai
import pandas as pd
import os
import requests
import random
import yaml


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


def wp_post(result, product):
    results = result.split("\n")

    title = results[0]
    final_text = ""
    for i in range(2, len(results)):
        final_text += results[i] + "<br>"

    # rewrite the final text using gemini
    print("Rewriting the final text")
    final_prompt = """
        Rewrite the following text to make it more engaging and informative:
        Use third person view
        Use <h2> for subheaders
        The output must be in HTML format
    """
    improved_text = final_text  # improve_response(final_prompt, final_text)
    
    if improved_text == "":
        improved_text = final_text
    # Upload to wordpress

    import requests
    from requests.auth import HTTPBasicAuth

    # Login credentials
    login = os.getenv('wp_login')
    password = os.getenv('wp_password')

    # URL to send the POST request to
    url = os.getenv('wp_url')
    
    affiliate_url = product['link']

    prompt = "Provide a very short rephrased version of the call to action, like act now, order now, get it now, etc, that maintains a direct and imperative tone suitable for a marketing context."
    cta_words = improve_response(prompt, "Order Now!")
    
    summarize_prompt = "Provide a short summary containing only 10 words or less that highlights the main benefits of the product."
    meta_desc = improve_response(summarize_prompt, final_text)

    cta_button = f"""
        <p>
        <div class="wp-block-buttons is-layout-flex wp-block-buttons-is-layout-flex">
        <div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="{affiliate_url}" target="_blank" rel="noopener">{cta_words}</a></div>
        </div>
    """

    improved_text += cta_button

    title = title.replace("Title: ", "")
    product_name = product['product']
    media_id = product['media_id']
    tag_id = product['tag_id']
    if product['type'] == 'supplement':
        tags = [4, int(tag_id), 5]
    elif product['type'] == 'book':
        tags = [54, int(tag_id), 5]

    # Data for creating a new post
    data = {
        "title": title,
        "status": "publish",
        "content": improved_text,
        "comment_status": "closed",
        "ping_status": "closed",
        "featured_media": int(media_id),
        "tags": tags,
        "meta": {
            "rank_math_title": title,
            "rank_math_description": meta_desc,
            "rank_math_focus_keyword": product_name
        }
    }

    # Make the POST request with basic authentication
    response = requests.post(url, auth=HTTPBasicAuth(login, password), json=data)
    return response


def product_review_random():
    product = pd.read_csv("products/products_all.csv")
    num_posts = random.randint(30, 40)
    print(f"Will be creating {num_posts} number of posts")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    yaml_file_path = os.path.join(script_dir, 'config', 'review_details.yaml')
    with open(yaml_file_path, 'r') as file:
        details_dict = yaml.safe_load(file)

    for i in range(0, num_posts):
        try:
            print(f"Preparing post number {i}")
            idx_rand = random.randint(0, len(product)-1)
            product_type = product['type'][idx_rand]
            details = details_dict[product_type]['details']
            product_name = product['product'][idx_rand] + f' {product_type}'
            inputs = {
                'topic': product_name,
                'details': details,
            }
            result = ProductReviewCrew().crew('soft_selling').kickoff(inputs=inputs)
            response = wp_post(result, product.iloc[idx_rand])
        except requests.exceptions.HTTPError as e:
            print(e)
            if response.status_code == 429:
                import time
                time.delay(60)


def product_review_new():
    product = pd.read_csv("products/products.csv")
    num_posts = product.shape[0]
    print(f"Will be creating {num_posts} number of posts")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    yaml_file_path = os.path.join(script_dir, 'config', 'review_details.yaml')
    with open(yaml_file_path, 'r') as file:
        details_dict = yaml.safe_load(file)

    idx_rand = 0
    for i in range(0, num_posts):
        try:
            print(f"Preparing post number {i}")
            product_type = product['type'][idx_rand]
            details = details_dict[product_type]['details']
            product_name = product['product'][idx_rand] + f' {product_type}'
            inputs = {
                'topic': product_name,
                'details': details,
            }
            result = ProductReviewCrew().crew('soft_selling').kickoff(inputs=inputs)
            response = wp_post(result, product.iloc[idx_rand])
            idx_rand += 1
        except requests.exceptions.HTTPError as e:
            print(e)
            if response.status_code == 429:
                import time
                time.delay(60)


def test():
    inputs = {
        'topic': 'The Essential Keto Cookbook',
    }
    result = ProductReviewCrew().crew('test').kickoff(inputs=inputs)
    print(result)


def run():
    # test()
    # product_review_new()
    product_review_random()


if __name__ == '--main__':
    run()

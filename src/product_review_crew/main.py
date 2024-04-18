from dotenv import load_dotenv
from product_review_crew.crew import ProductReviewCrew
import google.generativeai as genai
import pandas as pd
import os
import requests
import random


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

    cta_button = f"""
        <p>
        <div class="wp-block-buttons is-layout-flex wp-block-buttons-is-layout-flex">
        <div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="{affiliate_url}" target="_blank" rel="noopener">{cta_words}</a></div>
        </div>
    """

    final_text += cta_button

    title = title.replace("Title: ", "")
    media_id = product['media_id']
    tag_id = product['tag_id']
    if product['type'] == 'supplement':
        tags = [4, int(tag_id), 5]
    elif product['type'] == 'book':
        tags = [54, int(tag_id), 5]

    # Data for creating a new post
    data = {
        "title": title,
        "status": "draft",
        "content": final_text,
        "comment_status": "closed",
        "ping_status": "closed",
        "featured_media": int(media_id),
        "tags": tags,
    }

    # Make the POST request with basic authentication
    response = requests.post(url, auth=HTTPBasicAuth(login, password), json=data)
    return response


def product_review_random():
    product = pd.read_csv("products/products_all.csv")
    num_posts = random.randint(30, 40)
    print(f"Will be creating {num_posts} number of posts")

    for i in range(0, num_posts):
        try:
            print(f"Preparing post number {i}")
            idx_rand = random.randint(0, len(product)-1)
            product_type = product['type'][idx_rand]
            if product_type == 'supplement':
                details = """
                        product information, purpose and claim, effectiveness,
                        ingredients, side effects, value for money and 
                        customer reviews
                    """
            elif product_type == 'book':
                details = """
                        book information, summary, effectiveness, critique,
                        audience, educational value, impact,
                        value for money and customer reviews
                    """
            product_name = product['product'][idx_rand] + f' {product_type}'
            inputs = {
                'topic': product_name,
                'details': details,
            }
            result = ProductReviewCrew().crew('product').kickoff(inputs=inputs)
            response = wp_post(result, product.iloc[idx_rand])
        except requests.exceptions.HTTPError as e:
            print(e)
            if response.status_code == 429:
                import time
                time.delay(60)


def product_review_new():
    product = pd.read_csv("products/products.csv")
    num_posts = product.shape[0] - 1
    print(f"Will be creating {num_posts} number of posts")

    idx_rand = 0
    for i in range(0, num_posts):
        try:
            print(f"Preparing post number {i}")
            product_type = product['type'][idx_rand]
            if product_type == 'supplement':
                details = """
                        product information, purpose and claim, effectiveness,
                        ingredients, side effects, value for money and
                        customer reviews
                    """
            elif product_type == 'book':
                details = """
                        book information, summary, effectiveness, critique,
                        audience, educational value, impact,
                        value for money and customer reviews
                    """
            product_name = product['product'][idx_rand] + f' {product_type}'
            inputs = {
                'topic': product_name,
                'details': details,
            }
            result = ProductReviewCrew().crew('product').kickoff(inputs=inputs)
            response = wp_post(result, product.iloc[idx_rand])
            idx_rand += 1
        except requests.exceptions.HTTPError as e:
            print(e)
            if response.status_code == 429:
                import time
                time.delay(60)


def run():
    product_review_new()


if __name__ == '--main__':
    run()

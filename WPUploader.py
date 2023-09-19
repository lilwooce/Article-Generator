import requests
import base64
import json
from wordpress import API
from datetime import datetime
from slugify import slugify
import streamlit as st

username = "protheus99@gmail.com"
password = "Mroq tBu0 kLOW z0d8 oP4p 3LfA"

wordpress_credentials = username + ":" + password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8'), 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}


# Your WordPress site URL
site_url = 'https://shop.genbc.io'
# Your WordPress username
username = 'protheus99@gmail.com'
# The application password you generated
password = 'Mroq tBu0 kLOW z0d8 oP4p 3LfA'
def create_category(category_name, parent='None'):
    # Check if the category already exists
    url = f'{site_url}/wp-json/wp/v2/categories?search={category_name}'
    response = requests.get(url, auth=(username, password))
    
    if response.status_code == 200:
        categories = json.loads(response.text)
        for category in categories:
            if category['name'].lower() == category_name.lower():
                st.write(f"Category '{category_name}' already exists")
                return category['id']
    
    # The category doesn't exist, so create it
    url = f'{site_url}/wp-json/wp/v2/categories'
    data = {
        'name': category_name,
        'parent': parent
    }
    response = requests.post(url, auth=(username, password), json=data)
    
    if response.status_code == 201:
        category = json.loads(response.text)
        st.write(f"Category '{category_name}' created successfully")
        return category['id']
    else:
        st.write(f"Failed to create category '{category_name}': {response.text}")
        return None
# Test the function


def createWPPost(article, title, categories):
    st.write("creating wordpress post")
    api_url = 'https://shop.genbc.io/wp-json/wp/v2/posts/'
    article = open(article)
    data = {
    'title' : title,
    'content' : article.read(),
    'status' : 'publish', 
    'categories': categories,
    'date' : str(datetime.now()),
    'slug' : slugify(title),
    }
    response = requests.post(api_url, headers=wordpress_header, json=data)
    st.write(response)

def createWPCategory(name, parentID="None"):
    st.write("creating wordpress category")
    st.write()
    api_url = 'https://shop.genbc.io/wp-json/wp/v2/categories'
    data = {
        'name': name,
        'slug': slugify(name),
        'parent': parentID
    }
    response = requests.post(api_url, headers=wordpress_header, json=data)
    st.write(response)
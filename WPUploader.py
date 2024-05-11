import requests
import base64
import json
from wordpress import API
from datetime import datetime
from slugify import slugify
import streamlit as st

username = st.secrets['username']
password = st.secrets['password']
wordpress_credentials = username + ":" + password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8'), 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}


def createWPPost(article, title, categories):
    st.write("creating wordpress post")
    api_url = 'https://shop.genbc.io/wp-json/wp/v2/posts/'
    data = {
    'title' : title,
    'content' : article,
    'status' : 'publish', 
    'categories': categories,
    'date' : str(datetime.now()),
    'slug' : slugify(title),
    }
    
    response = requests.post(api_url, headers=wordpress_header, json=data)
    if response.status_code == 201:
        post = json.loads(response.text)
        st.write(f"Post '{title}' created successfully")
        st.write(f"The link to the {title} post is {post['link']}")
        return post['id']
    else:
        st.write(f"Failed to create post '{title}': {response.text}")
        return None

def createWPCategory(name, parentID=None):
    # Check if the category already exists
    url = f'https://shop.genbc.io/wp-json/wp/v2/categories?search={name}'
    response = requests.get(url, headers=wordpress_header)
    
    if response.status_code == 200:
        categories = json.loads(response.text)
        for category in categories:
            if category['name'].lower() == name.lower():
                st.write(f"Category '{name}' already exists")
                return category['id']
            
    st.write("creating wordpress category")
    api_url = 'https://shop.genbc.io/wp-json/wp/v2/categories'
    data = {
        'name': name,
        'slug': slugify(name),
        'parent': parentID
    }
    response = requests.post(api_url, headers=wordpress_header, json=data)
    if response.status_code == 201:
        category = json.loads(response.text)
        st.write(f"Category '{name}' created successfully")
        return category['id']
    else:
        st.write(f"Failed to create category '{name}': {response.text}")
        return None
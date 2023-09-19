import requests
import base64
import json
from wordpress import API
from datetime import datetime
from slugify import slugify
import streamlit as st

username = "protheus99@gmail.com"
password = "mymf dsA0 V8o2 c4BQ SIan pywi"
#mBjE xlA6 fBsv SZ8k MgqT Udql
#ycUa Ym1N Nya6 C6DJ cISU PyQ1
#Mroq tBu0 kLOW z0d8 oP4p 3LfA
#bPUx nRux bJXP k3SS xKCQ Zdy0
#RMP3 cfy0 luKu lNWU tQdp D7dS
#mymf dsA0 V8o2 c4BQ SIan pywi

wordpress_credentials = username + ":" + password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8'), 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}


def createWPPost(article, title, categories):
    st.write("creating wordpress post")
    api_url = 'https://shop.genbc.io/wp-json/wp/v2/posts/'
    st.write(article)
    data = {
    'title' : title,
    'content' : article.read(),
    'status' : 'publish', 
    'categories': categories,
    'date' : str(datetime.now()),
    'slug' : slugify(title),
    }
    response = requests.post(api_url, headers=wordpress_header, json=data)
    if response.status_code == 201:
        category = json.loads(response.text)
        st.write(f"Post '{title}' created successfully")
        return category['id']
    else:
        st.write(f"Failed to create post '{title}': {response.text}")
        return None

def createWPCategory(name, parentID=None):
    st.write("creating wordpress category")
    st.write()
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
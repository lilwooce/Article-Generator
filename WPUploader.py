import requests
import base64
import json
import wordpress
from wordpress import API
from datetime import datetime
from slugify import slugify

username = "protheus99@gmail.com"
password = "Mroq tBu0 kLOW z0d8 oP4p 3LfA"

wordpress_credentials = username + ":" + password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8'), 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}


def createWPPost(article, title, categories):
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
    response = requests.post(api_url,headers=wordpress_header, json=data)
    print(response)

def createWPCategory(name, parentID="None"):
    api_url = 'https://shop.genbc.io/wp-json/wp/v2/categories'
    data = {
        'name': name,
        'slug': slugify(name),
        'parent': parentID
    }
    response = requests.post(api_url, headers=wordpress_header, json=data)
    print(response)

createWPPost()
# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd


# Define a function to scrape Google search results and create a dataframe
def scrape_google(query):
    # Set headers to mimic a web browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    # Build the URL with the query parameter
    url = f'https://www.google.com/search?q={query}'
    # Send a request to the URL and store the HTML content
    html = requests.get(url, headers=headers).content
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    # Find all the search result elements
    search_results = soup.find_all('div') #changed from only getting divs with class 'g'
    # Initialize an empty list to store the search results
    results = []
    # Loop through each search result and extract the relevant information
    for result in search_results:
        try:
            title = result.find('h3').text
            url = result.find('a')['href']
            results.append((title, url))
        except:
            continue
    # Create a dataframe from the search results
    df = pd.DataFrame(results, columns=['Title', 'URL'])
    df.to_csv("Scraped_URLs_From_SERPS.csv")
    return df

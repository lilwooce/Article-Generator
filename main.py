# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
import newspaper
from newspaper import Article
import nltk
import statistics
import collections
from nltk.collocations import TrigramAssocMeasures, TrigramCollocationFinder
from nltk.collocations import QuadgramAssocMeasures, QuadgramCollocationFinder
from pytrends.request import TrendReq



# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('tagsets')
# nltk.download('words')
# nltk.download('maxent_ne_chunker')
# nltk.download('vader_lexicon')
# nltk.download('inaugural')
# nltk.download('webtext')
# nltk.download('treebank')
# nltk.download('gutenberg')
# nltk.download('genesis')


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

def relQueries(query):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(kw_list=[query], cat=184, timeframe="today 12-m")
    relTop = pytrends.related_topics()
    topRelated = relTop.get(query).get('top')
    topTopics = topRelated['topic_title'].explode().to_list()
    return topTopics

def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""



# Define a function to perform NLP analysis and return a string of keyness results
def analyze_text(text):
    # Tokenize the text and remove stop words
    tokens = [word.lower() for word in word_tokenize(text) if word.isalpha() and word.lower() not in stopwords.words('english')]
    # Get the frequency distribution of the tokens
    fdist = FreqDist(tokens)
    # Create a bigram finder and get the top 20 bigrams by keyness
    bigram_measures = BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(tokens)
    bigrams = finder.nbest(bigram_measures.raw_freq, 20)
    # Create a string from the keyness results
    results_str = ''
    results_str += 'Top 20 Words:\n'
    for word, freq in fdist.most_common(20):
        results_str += f'{word}: {freq}\n'
    results_str += '\nTop 20 Bigrams:\n'
    for bigram in bigrams:
        results_str += f'{bigram[0]} {bigram[1]}\n'
    return results_str

# Define the main function to scrape Google search results and analyze the article text
def main(query):
    # Scrape Google search results and create a dataframe
    df = scrape_google(query)
    # Scrape article text for each search result and store it in the dataframe
    for index, row in df.iterrows():
        url = row['URL']
        article_text = scrape_article(url)
        df.at[index, 'Article Text'] = article_text
    # Analyze the article text for each search result and store the keyness results in the dataframe
    for index, row in df.iterrows():
        text = row['Article Text']
        keyness_results = analyze_text(text)
        df.at[index, 'Keyness Results'] = keyness_results
    # Return the final dataframe
    df.to_csv("NLP_Data_On_SERP_Links_Text.csv")
    return df



# Define the main function to scrape Google search results and analyze the article text
def analyze_serps(query):
    # Scrape Google search results and create a dataframe
    df = scrape_google(query)
    # Scrape article text for each search result and store it in the dataframe
    for index, row in df.iterrows():
        url = row['URL']
        article_text = scrape_article(url)
        df.at[index, 'Article Text'] = article_text
    # Analyze the article text for each search result and store the NLP results in the dataframe
    for index, row in df.iterrows():
        text = row['Article Text']
        # Tokenize the text and remove stop words
        tokens = [word.lower() for word in word_tokenize(text) if word.isalpha() and word.lower() not in stopwords.words('english') and 'contact' not in word.lower() and 'admin' not in word.lower()]
        # Calculate the frequency distribution of the tokens
        fdist = FreqDist(tokens)
        # Calculate the 20 most common words
        most_common = fdist.most_common(20)
        # Calculate the 20 least common words
        least_common = fdist.most_common()[-20:]
        # Calculate the 20 most common bigrams
        bigram_measures = BigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(tokens)
        bigrams = finder.nbest(bigram_measures.raw_freq, 20)
        # Calculate the 20 most common trigrams
        trigram_measures = TrigramAssocMeasures()
        finder = TrigramCollocationFinder.from_words(tokens)
        trigrams = finder.nbest(trigram_measures.raw_freq, 20)
        # Calculate the 20 most common quadgrams
        quadgram_measures = QuadgramAssocMeasures()
        finder = QuadgramCollocationFinder.from_words(tokens)
        quadgrams = finder.nbest(quadgram_measures.raw_freq, 20)
        # Calculate the part-of-speech tags for the text
        pos_tags = nltk.pos_tag(tokens)
        # Store the NLP results in the dataframe
        df.at[index, 'Most Common Words'] = ', '.join([word[0] for word in most_common])
        df.at[index, 'Least Common Words'] = ', '.join([word[0] for word in least_common])
        df.at[index, 'Most Common Bigrams'] = ', '.join([f'{bigram[0]} {bigram[1]}' for bigram in bigrams])
        df.at[index, 'Most Common Trigrams'] = ', '.join([f'{trigram[0]} {trigram[1]} {trigram[2]}' for trigram in trigrams])
        df.at[index, 'Most Common Quadgrams'] = ', '.join([f'{quadgram[0]} {quadgram[1]} {quadgram[2]} {quadgram[3]}' for quadgram in quadgrams])
        df.at[index, 'POS Tags'] = ', '.join([f'{token}/{tag}' for token, tag in pos_tags])
        # Replace any remaining commas with spaces in the Article Text column
        df.at[index, 'Article Text'] = ' '.join(row['Article Text'].replace(',', ' ').split())
    # Save the final dataframe as an Excel file
    writer = pd.ExcelWriter('NLP_Based_SERP_Results.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()
    # Return the final dataframe
    return df




# Define a function to summarize the NLP results from the dataframe
def summarize_nlp(df):
    # Calculate the total number of search results
    total_results = len(df)
    # Calculate the average length of the article text
    avg_length = round(df['Article Text'].apply(len).mean(), 2)
    # Get the most common words across all search results
    all_words = ', '.join(df['Most Common Words'].sum().split(', '))
    # Get the most common bigrams across all search results
    all_bigrams = ', '.join(df['Most Common Bigrams'].sum().split(', '))
    # Get the most common trigrams across all search results
    all_trigrams = ', '.join(df['Most Common Trigrams'].sum().split(', '))
    # Get the most common quadgrams across all search results
    all_quadgrams = ', '.join(df['Most Common Quadgrams'].sum().split(', '))
    # Get the most common part-of-speech tags across all search results
    all_tags = ', '.join(df['POS Tags'].sum().split(', '))
    # Calculate the median number of words in the article text
    median_words = statistics.median(df['Article Text'].apply(lambda x: len(x.split())).tolist())
    # Calculate the frequency of each word across all search results
    word_freqs = collections.Counter(all_words.split(', '))
    # Calculate the frequency of each bigram across all search results
    bigram_freqs = collections.Counter(all_bigrams.split(', '))
    # Calculate the frequency of each trigram across all search results
    trigram_freqs = collections.Counter(all_trigrams.split(', '))
    # Calculate the frequency of each quadgram across all search results
    quadgram_freqs = collections.Counter(all_quadgrams.split(', '))
    # Calculate the top 20% of most frequent words
    top_words = ', '.join([word[0] for word in word_freqs.most_common(int(len(word_freqs) * 0.2))])
    # Calculate the top 20% of most frequent bigrams
    top_bigrams = ', '.join([bigram[0] for bigram in bigram_freqs.most_common(int(len(bigram_freqs) * 0.2))])
    # Calculate the top 20% of most frequent trigrams
    top_trigrams = ', '.join([trigram[0] for trigram in trigram_freqs.most_common(int(len(trigram_freqs) * 0.2))])
    # Calculate the top 20% of most frequent quadgrams
    top_quadgrams = ', '.join([quadgram[0] for quadgram in quadgram_freqs.most_common(int(len(quadgram_freqs) * 0.2))])
    
    #print(f'Total results: {total_results}')
    #print(f'Average article length: {avg_length} characters')
    #print(f'Median words per article: {median_words}')
    #print(f'Most common words: {top_words} ({len(word_freqs)} total words)')
    #print(f'Most common bigrams: {top_bigrams} ({len(bigram_freqs)} total bigrams)')
    #print(f'Most common trigrams: {top_trigrams} ({len(trigram_freqs)} total trigrams)')
    #print(f'Most common quadgrams: {top_quadgrams} ({len(quadgram_freqs)} total quadgrams)')
    #print(f'Most common part-of-speech tags: {all_tags}')
    summary = ""
    summary += f'Total results: {total_results}\n'
    summary += f'Average article length: {avg_length} characters\n'
    summary += f'Median words per article: {median_words}\n'
    summary += f'Most common words: {top_words} ({len(word_freqs)} total words)\n'
    summary += f'Most common bigrams: {top_bigrams} ({len(bigram_freqs)} total bigrams)\n'
    summary += f'Most common trigrams: {top_trigrams} ({len(trigram_freqs)} total trigrams)\n'
    summary += f'Most common quadgrams: {top_quadgrams} ({len(quadgram_freqs)} total quadgrams)\n'
    return summary


from openai import OpenAI
import pandas as pd
import re
import time
import asyncio
import streamlit as st
import random
from IPython.display import display, Markdown
from main import *
from ast import literal_eval
import zipfile

client = OpenAI(
    api_key = st.secrets["OPENAI_API_KEY"]
)

def save_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write("\n".join(content))

def generate_content(prompt, model="gpt-3.5-turbo", max_tokens=2000, temperature=0.4):
    gpt_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Simulate an exceptionally talented journalist and editor. Given the following instructions, think step by step and produce the best possible output you can."},
            {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=temperature,
    )
    response = gpt_response.choices[0].message.content
    return response.strip().split('\n')

def quickArticleCreate(qry, model="gpt-3.5-turbo-16k", max_tokens=3000):
    filename = f"{qry[0:75]}{random.randint(1,100000000)}.txt"
    prompt = f"Act as a skilled content writer who is proficient in SEO writing and has excellent English language skills. To get started, please create two tables. The first table should contain an outline of the article, and the second table should contain the article itself. Please use Markdown language to bold the heading of the second table. The article should be 4,000 words long, unique, SEO-optimized, and human-written in English. It should cover the given topic and include at least 15 headings and subheadings (including H1, H2, H3, and H4 headings). Please compose the article in your own words, avoiding copying and pasting from other sources. When producing content, each paragraph should be at least 250 words long, please consider complexity and burstiness, striving to achieve high levels of both without sacrificing specificity or context. Use paragraphs that fully engage the reader, and write in a conversational style that is human-like. This means employing an informal tone, utilizing personal pronouns, keeping it simple, engaging the reader, utilizing the active voice, keeping it brief, asking rhetorical questions, and incorporating analogies and metaphors. Please end the article with a conclusion paragraph and 5 unique FAQs after the conclusion. Additionally, remember to bold the title and all headings of the article and use appropriate headings for H tags. Now, please write an article on the given topic: {qry}"
    article = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file(filename, article)
    st.write(f"{filename}has been created")
    return(filename)

def genFiles():
    st.write("generating files")

    for t in st.session_state.multiGenTopics:
        st.write(f"generating article {t}")
        article = quickArticleCreate(t)
        with open(article, "rb") as file:
            st.download_button(label=f"Download {t}", data=file, file_name="final_data.zip", key=f"{t}")
        file.close()

def main():
    st.set_page_config(
        page_icon="📝", 
        page_title="Create a multiple downloadable articles zipped into a single file"
    )

    st.text("Add or upload the topics of the articles you want to generate below")

    data = st.file_uploader("uplaod file", type={"csv", "txt"})
    df = pd.DataFrame(columns=["Topic"])
    editedDF = st.data_editor(df, num_rows="dynamic")
    if data is not None:
        editedDF = pd.read_csv(data)
        st.write(editedDF)
    
    submitted = st.button("Submit")
    if submitted:
        st.session_state.multiGenTopics = editedDF["Topic"].tolist()
        st.write(st.session_state.multiGenTopics)
        genFiles()
        

        
                

        
    
main()
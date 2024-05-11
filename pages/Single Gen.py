from openai import OpenAI
import pandas as pd
import re
import time
import asyncio
import streamlit as st
from IPython.display import display, Markdown
from main import *
from ast import literal_eval
import json
import WPUploader
import anthropic

client = anthropic.Anthropic(
    api_key=st.secrets["CLAUDE_API_KEY"],
)

def save_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write("\n".join(content))

def generate_content(prompt, model="claude-3-opus-20240229", max_tokens=1000, temperature=0.4):
    message = client.messages.create(
        model="model",
        max_tokens=max_tokens,
        temperature=temperature,
        system=f"Acting as a website copywriter with over 25 years of experience, create content for the following topic {prompt}. For the topic create a Meta title that follows the rules described. Use the following rules when creating a meta title: Title length should be between 50 to 60. To target unique user searches, use keyword phrases instead of keywords. A specialist toy company might include the keyword phrase 'Japanese Anime Toys' instead of the generic keyword 'Toys'. The page title should convey the essence of the page and be readable. Do not overfill the title with keywords; just one or two phrases in the visible part will be enough. As much as possible do not use stop words in titles. Meta description. Use the following rules when creating a meta description: Use approximately 25 - 30 words, 105 to 150 Characters in Length. Include important keywords used on the page within the Description. If the page content focuses on 2 core keyword phrases, write one sentence for each keyword phrase. focus the description based on the search intent of the customer. Search intents are: Navigational, Informational, Commercial, and Transactional Page header. Use the following rules when creating the header: The header should be between 40-50 characters. The words in the header should reinforce the topic. Page sub header. Sub header will reinforce the header and actions. Use the following rules for sub headers: Grab Attention With Descriptive Subheadings, Use Keywords To Help With SEO Performance. Use Parallel Structure in Your Subheadings. 300 words of page content using the AIDA Attention Interest Desire Action framework. One paragraph each for Attention, Interest, Desire, Action. 50 word summary of the content and call to action.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content

def generate_semantic_improvements_guide(prompt,query, model="claude-3-opus-20240229", max_tokens=1000, temperature=0.4):
    message = client.messages.create(
        model="model",
        max_tokens=max_tokens,
        temperature=temperature,
        system=f"You are an expert at Semantic SEO. In particular, you are superhuman at taking the result of an NLP keyword analysis of a search engine results page for a given keyword, and using it to build a readout/guide that can be used to inform someone writing a long-form article about a given topic so that they can best fully cover the semantic SEO as shown in the SERP. The goal of this guide is to help the writer make sure that the content they are creating is as comprehensive to the semantic SEO expressed in the content that ranks on the first page of Google for the given query. With the following semantic data, please provide this readout/guide. This readout/guide should be useful to someone writing about the topic, and should not include instructions to add info to the article about the SERP itself. The SERP semantic SEO data is just to be used to help inform the guide/readout. Please provide the readout/guide in well organized and hierarchical markdown.",
        messages=[
            {"role": "user", "content": "Semantic SEO data for the keyword based on the content that ranks on the first page of google for the given keyword query of: {query} and it's related semantic data:  {prompt}"}
        ]
    )
    save_to_file("Semantic_SEO_Readout.txt", message.content)
    return message.content   

def generate_outline(topic, model="claude-3-opus-20240229", max_tokens=500):
    prompt = f"Generate an incredibly thorough article outline for the topic: {topic}. Consider all possible angles and be as thorough as possible. Please use Roman Numerals for each section."
    outline = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file("outline.txt", outline)
    return outline

def improve_outline(outline, semantic_readout, model="claude-3-opus-20240229", max_tokens=1000):
    prompt = f"Given the following article outline, please improve and extend this outline significantly. Please use Roman Numerals for each section. The goal is as thorough, clear, and useful out line as possible exploring the topic in as much depth as possible. Think step by step before answering. Please take into consideration the semantic seo readout provided here: {semantic_readout} which should help inform some of the improvements you can make, though please also consider additional improvements not included in this semantic seo readout.  Outline to improve: {outline}."
    improved_outline = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file("improved_outline.txt", improved_outline)
    return improved_outline



def generate_sections(improved_outline, model="claude-3-opus-20240229", max_tokens=250):
    sections = []

    # Parse the outline to identify the major sections
    major_sections = []
    current_section = []
    for part in improved_outline:
        if re.match(r'^[ \t]*[#]*[ \t]*(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV)\b', part):
            if current_section:  # not the first section
                major_sections.append('\n'.join(current_section))
                current_section = []
        current_section.append(part)
    if current_section:  # Append the last section
        major_sections.append('\n'.join(current_section))

    # Generate content for each major section
    for i, section_outline in enumerate(major_sections):
        full_outline = "Given the full improved outline: "
        full_outline += '\n'.join(improved_outline)
        specific_section = ", and focusing specifically on the following section: "
        specific_section += section_outline
        prompt = full_outline + specific_section + ", please write a thorough part of the article that goes in-depth, provides detail and evidence, and adds as much additional value as possible. Section text:"
        section = generate_content(prompt, model=model, max_tokens=max_tokens)
        sections.append(section)
        save_to_file(f"section_{i+1}.txt", section)
    return sections



def improve_section(section, i, model="claude-3-opus-20240229", max_tokens=500):
    prompt = f"Given the following section of the article: {section}, please make thorough and improvements to this section. Only provide the updated section, not the text of your recommendation, just make the changes. Provide the updated section in Markdown please. Updated Section with improvements:"
    improved_section = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file(f"improved_section_{i+1}.txt", improved_section)
    return " ".join(improved_section)  # join the lines into a single string






def concatenate_files(file_names, output_file_name):
    final_draft = ''
    
    for file_name in file_names:
        with open(file_name, 'r') as file:
            final_draft += file.read() + "\n\n"  # Add two newline characters between sections

    with open(output_file_name, 'w') as output_file:
        output_file.write(final_draft)
    return final_draft

def generate_custom_content(prompt, model="claude-3-opus-20240229", max_tokens=3200, temperature=0.4):
    message = client.messages.create(
        model="model",
        max_tokens=max_tokens,
        temperature=temperature,
        system=f"Acting as a website copywriter with over 25 years of experience, create content for the following topic {prompt}. For the topic create a Meta title that follows the rules described. Use the following rules when creating a meta title: Title length should be between 50 to 60. To target unique user searches, use keyword phrases instead of keywords. A specialist toy company might include the keyword phrase 'Japanese Anime Toys' instead of the generic keyword 'Toys'. The page title should convey the essence of the page and be readable. Do not overfill the title with keywords; just one or two phrases in the visible part will be enough. As much as possible do not use stop words in titles. Meta description. Use the following rules when creating a meta description: Use approximately 25 - 30 words, 105 to 150 Characters in Length. Include important keywords used on the page within the Description. If the page content focuses on 2 core keyword phrases, write one sentence for each keyword phrase. focus the description based on the search intent of the customer. Search intents are: Navigational, Informational, Commercial, and Transactional Page header. Use the following rules when creating the header: The header should be between 40-50 characters. The words in the header should reinforce the topic. Page sub header. Sub header will reinforce the header and actions. Use the following rules for sub headers: Grab Attention With Descriptive Subheadings, Use Keywords To Help With SEO Performance. Use Parallel Structure in Your Subheadings. 300 words of page content using the AIDA Attention Interest Desire Action framework. One paragraph each for Attention, Interest, Desire, Action. 50 word summary of the content and call to action.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content

def quickArticle(qry, model="claude-3-opus-20240229"):
    a = generate_custom_content(qry, model)
    save_to_file("article.txt", a)
    with open("article.txt") as file:
        st.download_button(label=f"Download Final Draft ({qry})", data=file, key=qry)
    return a

def createArticle(qry, model="claude-3-opus-20240229", max_tokens_outline=1000, max_tokens_section=2000, max_tokens_improve_section=2000):
    query = qry
    results = analyze_serps(query)
    summary = summarize_nlp(results)

    semantic_readout = generate_semantic_improvements_guide(qry, summary,  model=model, max_tokens=max_tokens_outline)
    

    print(f"Topic: {qry}\n")

    print(f"Semantic SEO Readout:")

    print("Generating initial outline...")
    initial_outline = generate_outline(qry, model=model, max_tokens=max_tokens_outline)
    '''with open("outline.txt") as file:
        st.download_button(label=f"Initial Outline ({qry})", data=file, key=f"IO {qry}")'''
    print("Initial outline created.\n")

    print("Improving the initial outline...")
    improved_outline = improve_outline(initial_outline, semantic_readout, model='claude-3-opus-20240229', max_tokens=500)
    print("Improved outline created.\n")

    print("Generating sections based on the improved outline...")
    sections = generate_sections(improved_outline, model=model, max_tokens=max_tokens_section)
    print("Sections created.\n")

    print("Improving sections...")
    file_names = [f"improved_section_{i+1}.txt" for i in range(len(sections))]
    for i, section in enumerate(sections):
        improve_section(section, i, model='claude-3-opus-20240229', max_tokens=1000)
    print("Improved sections created.\n")

    print("Creating final draft...")
    final_draft = concatenate_files(file_names, "final_draft.txt")
    with open("final_draft.txt") as file:
        st.download_button(label=f"Download Final Draft ({qry})", data=file, key=qry)
    return final_draft

def generateCategories(qry, numCats, model="claude-3-opus-20240229", max_tokens=500):
    prompt = f"Given the following query: {qry}, please provide 5 categories that would fit into a wordpress article of the same topic. The topics must differ from eachother and must also be related to the main query provided. Provide the categories in a python array format so that I can define the output provided as a python array variable with no extra formatting on my part. For example, a good response that you must follow the format of if I gave you the prompt 'television' would be: ['Television Stores', 'Television Deals', 'Television Repair', 'Wall Television Installation', 'Television Shows', 'Television Remotes', 'Televisions For Home Use'] The response MUST include BOTH the questions AND the topics in the format provided. ENSURE THAT THE FORMATTING IS PROPER AND THERE ARE NO EXTRA BRACKETS/QUOTATION MARKS OR ANYTHING OF THE SORT. ALSO ENSURE THAT THERE ARE NO QUOTATION MARKS IN THE QUESTIONS THEMSELVES EX: won't should be changed to wont. IF THERE ARE THEY MUST BE REMOVED."
    categoryArray = generate_content(prompt, model=model, max_tokens=max_tokens)
    return categoryArray

def generateSubTopics(qry, numArticles, model="claude-3-opus-20240229", max_tokens=500): 
    prompt = f"Given the following query: {qry}, please provide 5 questions that people also ask. The questions must differ from eachother and must also be related to the main query provided. Also provide 5 related topics to the main topic. The topics must differ from eachother and must also be related to the main query provided Provide the questions and topics in a python array format so that I can define the output provided as a python array variable with no extra formatting on my part. For example, a good response that you must follow the format of if I gave you the prompt 'fly fishing in colorado' would be: ['colorado', 'wyoming', 'montana', 'alaska', 'bahamas', 'Where is fly fishing the most popular?', 'What state has best fly fishing?', Where is the best place to learn fly fishing?, What is the fly fishing capital of the world?, What is a famous quote about fly fishing?]. The response MUST include BOTH the questions AND the topics in the format provided. ENSURE THAT THE FORMATTING IS PROPER AND THERE ARE NO EXTRA BRACKETS/QUOTATION MARKS OR ANYTHING OF THE SORT. ALSO ENSURE THAT THERE ARE NO QUOTATION MARKS IN THE QUESTIONS THEMSELVES EX: won't should be changed to wont. IF THERE ARE THEY MUST BE REMOVED. MAKE SURE THAT THE FINAL RESULT IS PURELY THE ARRAY OF SUB TOPICS AND THERE IS NO EXTRA TEXT SUCH AS, questions = [array of text]."
    subTopicSent = generate_content(prompt, model=model, max_tokens=max_tokens)
    return subTopicSent

def main():
    st.set_page_config(
        page_icon="📝", 
        page_title="Create a single downloadable article"
    )

    qry = st.text_input(
        "What do you want the main topic of the article to be? v04\n",
        key="query",
    )


    if qry:
        article = quickArticle(qry)

        st.write(article)
    
main()
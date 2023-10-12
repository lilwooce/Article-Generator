import openai
import pandas as pd
import re
import time
import asyncio
import streamlit as st
from IPython.display import display, Markdown
from main import *
from ast import literal_eval
import WPUploader
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]


def save_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write("\n".join(content))

def generate_content(prompt, model="gpt-3.5-turbo", max_tokens=500, temperature=0.4):
    gpt_response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Simulate an exceptionally talented journalist and editor. Given the following instructions, think step by step and produce the best possible output you can."},
            {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=temperature,
    )
    response = gpt_response['choices'][0]['message']['content'].strip()
    #print(response)
    return response.strip().split('\n')

def generate_semantic_improvements_guide(prompt,query, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.4):
    gpt_response = openai.ChatCompletion.create(
        model=model,
        messages=[
            #this is the improvement prompt
            {"role": "system", "content": "You are an expert at Semantic SEO. In particular, you are superhuman at taking the result of an NLP keyword analysis of a search engine results page for a given keyword, and using it to build a readout/guide that can be used to inform someone writing a long-form article about a given topic so that they can best fully cover the semantic SEO as shown in the SERP. The goal of this guide is to help the writer make sure that the content they are creating is as comprehensive to the semantic SEO expressed in the content that ranks on the first page of Google for the given query. With the following semantic data, please provide this readout/guide. This readout/guide should be useful to someone writing about the topic, and should not include instructions to add info to the article about the SERP itself. The SERP semantic SEO data is just to be used to help inform the guide/readout. Please provide the readout/guide in well organized and hierarchical markdown."},
            {"role": "user", "content": f"Semantic SEO data for the keyword based on the content that ranks on the first page of google for the given keyword query of: {query} and it's related semantic data:  {prompt}"}],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=temperature,
    )
    response = gpt_response['choices'][0]['message']['content'].strip()
    #print(response)
    formatted_response = response.strip().split('\n')
    save_to_file("Semantic_SEO_Readout.txt", formatted_response)
    return response   

def generate_outline(topic, model="gpt-3.5-turbo", max_tokens=500):
    prompt = f"Generate an incredibly thorough article outline for the topic: {topic}. Consider all possible angles and be as thorough as possible. Please use Roman Numerals for each section."
    outline = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file("outline.txt", outline)
    return outline

def improve_outline(outline, semantic_readout, model="gpt-3.5-turbo", max_tokens=1000):
    prompt = f"Given the following article outline, please improve and extend this outline significantly. Please use Roman Numerals for each section. The goal is as thorough, clear, and useful out line as possible exploring the topic in as much depth as possible. Think step by step before answering. Please take into consideration the semantic seo readout provided here: {semantic_readout} which should help inform some of the improvements you can make, though please also consider additional improvements not included in this semantic seo readout.  Outline to improve: {outline}."
    improved_outline = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file("improved_outline.txt", improved_outline)
    return improved_outline



def generate_sections(improved_outline, model="gpt-3.5-turbo", max_tokens=250):
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



def improve_section(section, i, model="gpt-3.5-turbo-16k", max_tokens=500):
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

    print("Final draft created.\n")
    return final_draft

def createArticle(qry, model="gpt-3.5-turbo-16k", max_tokens_outline=250, max_tokens_section=500, max_tokens_improve_section=500):
    query = qry
    results = analyze_serps(query)
    summary = summarize_nlp(results)

    semantic_readout = generate_semantic_improvements_guide(qry, summary,  model=model, max_tokens=max_tokens_outline)
    

    print(f"Topic: {qry}\n")

    print(f"Semantic SEO Readout:")

    print("Generating initial outline...")
    initial_outline = generate_outline(qry, model=model, max_tokens=max_tokens_outline)
    with open("outline.txt") as file:
        st.download_button(label=f"Initial Outline ({qry})", data=file, key=f"IO {qry}")
    print("Initial outline created.\n")

    print("Improving the initial outline...")
    improved_outline = improve_outline(initial_outline, semantic_readout, model='gpt-3.5-turbo', max_tokens=500)
    print("Improved outline created.\n")

    print("Generating sections based on the improved outline...")
    sections = generate_sections(improved_outline, model=model, max_tokens=max_tokens_section)
    print("Sections created.\n")

    print("Improving sections...")
    file_names = [f"improved_section_{i+1}.txt" for i in range(len(sections))]
    for i, section in enumerate(sections):
        improve_section(section, i, model='gpt-3.5-turbo', max_tokens=1000)
    print("Improved sections created.\n")

    print("Creating final draft...")
    final_draft = concatenate_files(file_names, "final_draft.txt")
    with open("final_draft.txt") as file:
        st.download_button(label=f"Download Final Draft ({qry})", data=file, key=qry)
    return final_draft

def generateCategories(qry, model="gpt-3.5-turbo-16k", max_tokens=500):
    prompt = f"Given the following query: {qry}, please provide 7 categories that would fit into a wordpress article of the same topic. The topics must differ from eachother and must also be related to the main query provided. Provide the categories in a python array format so that I can define the output provided as a python array variable with no extra formatting on my part. For example, a good response that you must follow the format of if I gave you the prompt 'television' would be: ['Television Stores', 'Television Deals', 'Television Repair', 'Wall Television Installation', 'Television Shows', 'Television Remotes', 'Televisions For Home Use']"
    categoryArray = generate_content(prompt, model=model, max_tokens=max_tokens)
    return categoryArray

def generateSubTopics(qry, model="gpt-3.5-turbo-16k", max_tokens=500):
    prompt = f"Given the following query: {qry}, please provide 5 questions that people also ask. The questions must differ from eachother and must also be related to the main query provided. Also provide 5 related topics to the main topic. The topics must differ from eachother and must also be related to the main query provided Provide the questions and topics in a python array format so that I can define the output provided as a python array variable with no extra formatting on my part. For example, a good response that you must follow the format of if I gave you the prompt 'fly fishing destinations' would be: ['colorado', 'wyoming', 'montana', 'alaska', 'bahamas', 'Where is fly fishing the most popular?', 'What state has best fly fishing?', Where is the best place to learn fly fishing?, What is the fly fishing capital of the world?, What is a famous quote about fly fishing?]. The response MUST include BOTH the questions AND the topics in the format provided."
    subTopics = generate_content(prompt, model=model, max_tokens=max_tokens)
    return subTopics

def main():
    with st.form("Article Generator"):
        qry = st.text_input(
            "What do you want the main topic of the articles to be? v26\n",
            key="query",
        )

        if qry:
            st.title(f"Article about {qry}")  # add a title
            categories = generateCategories(qry)
            categories = literal_eval(categories[0])
            st.write(categories)
            
            with st.form("Category Select"):    
                choosenCategories = st.multiselect('Which of these categories would you like for the articles?', categories)

                submitted = st.form_submit_button(label="Submit")
                if submitted:
                    st.write(choosenCategories)

            #mainCat = WPUploader.createWPCategory(qry)
            #st.write(f"Main Category ID is {mainCat}")
            subTopics = []
            for cat in choosenCategories:
                subTopics = generateSubTopics(cat)
                subTopics = literal_eval(subTopics[0])
                st.write(subTopics)

                with st.form("Sub Topic Select"):
                    choosenTopics = st.multiselect(f"Which of these Sub Topics would you like for the category: {cat}")

                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        st.write(choosenTopics)
                #st.write(f"Creating article using the category {cat}")
                #subCat = WPUploader.createWPCategory(cat, mainCat)
                #a = createArticle(cat)
                #WPUploader.createWPPost(a, cat, [subCat])
                #asyncio.sleep(120)
            st.write()  # visualize my dataframe in the Streamlit app

    submitted = st.form_submit_button("Submit")
    if submitted:
        return
        #start generating articles
    
main()
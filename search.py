import openai
import pandas as pd
import re
import streamlit as st
from IPython.display import display, Markdown
from main import *
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]


def save_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write("\n".join(content))

def generate_content(prompt, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.4):
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

def generate_semantic_improvements_guide(prompt,query, model="gpt-3.5-turbo", max_tokens=2000, temperature=0.4):
    gpt_response = openai.ChatCompletion.create(
        model=model,
        messages=[
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

def generate_outline(topic, model="gpt-3.5-turbo", max_tokens=1000):
    prompt = f"Generate an incredibly thorough article outline for the topic: {topic}. Consider all possible angles and be as thorough as possible. Please use Roman Numerals for each section."
    outline = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file("outline.txt", outline)
    return outline

def improve_outline(outline, semantic_readout, model="gpt-3.5-turbo", max_tokens=1000):
    prompt = f"Given the following article outline, please improve and extend this outline significantly. Please use Roman Numerals for each section. The goal is as thorough, clear, and useful out line as possible exploring the topic in as much depth as possible. Think step by step before answering. Please take into consideration the semantic seo readout provided here: {semantic_readout} which should help inform some of the improvements you can make, though please also consider additional improvements not included in this semantic seo readout.  Outline to improve: {outline}."
    improved_outline = generate_content(prompt, model=model, max_tokens=max_tokens)
    save_to_file("improved_outline.txt", improved_outline)
    return improved_outline



def generate_sections(improved_outline, model="gpt-3.5-turbo", max_tokens=2000):
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



def improve_section(section, i, model="gpt-4", max_tokens=4000):
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



def main(model="gpt-4", max_tokens_outline=2000, max_tokens_section=2000, max_tokens_improve_section=4000):
    qry = st.text_input(
        "What do you want the topic of the article to be?\n",
        key="query",
    )

    if qry:
        st.title(f"Article about {qry}")  # add a title
        st.write()  # visualize my dataframe in the Streamlit app


    query = qry
    results = analyze_serps(query)
    summary = summarize_nlp(results)

    semantic_readout = generate_semantic_improvements_guide(qry, summary,  model=model, max_tokens=max_tokens_outline)
    

    print(f"Topic: {qry}\n")

    print(f"Semantic SEO Readout:")
    display(Markdown(str(semantic_readout)))

    print("Generating initial outline...")
    initial_outline = generate_outline(qry, model=model, max_tokens=max_tokens_outline)
    st.download_button('Initial Outline', file_names)
    st.write(initial_outline)
    print("Initial outline created.\n")

    print("Improving the initial outline...")
    improved_outline = improve_outline(initial_outline, semantic_readout, model='gpt-3.5-turbo', max_tokens=1800)
    print("Improved outline created.\n")

    print("Generating sections based on the improved outline...")
    sections = generate_sections(improved_outline, model=model, max_tokens=max_tokens_section)
    print("Sections created.\n")

    print("Improving sections...")
    file_names = [f"improved_section_{i+1}.txt" for i in range(len(sections))]
    for i, section in enumerate(sections):
        improve_section(section, i, model='gpt-3.5-turbo', max_tokens=2000)
    print("Improved sections created.\n")

    print("Creating final draft...")
    final_draft = concatenate_files(file_names, "final_draft.txt")
    display(Markdown(final_draft))

    st.download_button('Download Article', file_names)
    st.write(final_draft)
    return final_draft
    

main()
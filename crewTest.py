from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv

load_dotenv()
openAIKey = os.environ.get("OPENAI_API_KEY")

seed='Taylor Swift'
num=5

writer = Agent(
    role="Writer",
    goal='Write compelling and engaging blogs based on a given seed',
    backstory='Simulate an exceptionally talented journalist and editor. Given the following instructions, think step by step and produce the best possible output you can.',
    verbose=True,
    allow_delegation=False
)

editor = Agent(
    role='Editor',
    goal='Take in a piece of writing and edit it to become more human-like as well as more compelling and engaging to read.',
    backstory='You are a professional editor of 30 years and you know exactly how to edit a piece of writing so that it becomes incredibly human-like, compelling, and engaging.',
    verbose=True,
    allow_delegation=False
)

contentGenerator = Agent(
    role='Content Generator',
    goal='Take in a seed phrase and generate a given amount of categories that all connect to eachother and the seed phrase to be later put into a Wordpress article/blog.',
    backstory='You are a professional writer of 50 years and you know exactly what categories connect and meld with eachother to make a perfect series of articles.',
    verbose=True,
    allow_delegation=True
)

genCategories = Task(description=f"Given the following seed phrase, {seed} generate {num} categories that would fit into a Wordpress article/blog and give each of the 5 categories to a writer agent to write the article/blog post.", agent=contentGenerator)
outline = Task(description=f"Generate an incredibly thorough article outline for each of the category topics previously generated. Consider all possible angles and be as thorough as possible. Please use Roman Numerals for each section.", agent=writer)
improveOutline = Task(description=f"Given the following article outline, please improve and extend this outline significantly. Please use Roman Numerals for each section. The goal is as thorough, clear, and useful out line as possible exploring the topic in as much depth as possible. Think step by step before answering. Do this to each of the previously generated outlines.", agent=writer)
generateSections = Task(description='For each of the generated outlines, go through and write a thorough article that goes in-depth, provides detail and evidence, and adds as much additional value as possible. Ensure that the article is at least 2000 words long.', agent=writer)
finalEdit = Task(description='Given the previously written articles, edit the text in a way so that the final result is a very human-like, compelling, and engaging version of the initial post. Do this while keeping the overall meaning of the text as much of the same as possible.', agent=editor)

crew = Crew(
    agents=[writer, editor, contentGenerator],
    tasks=[genCategories, outline, improveOutline, generateSections, finalEdit],
    verbose=2,
    process=Process.sequential
)

result = crew.kickoff()

with open(f'finalDraft {seed}.txt', 'w') as output_file:
        output_file.write(result)
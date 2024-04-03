import os
from openai import OpenAI
import asyncio
import urllib.request
from bs4 import BeautifulSoup
import re
import requests
import tiktoken


os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain import OpenAI

from backend_url_selector import extract_url_from_page
# question = "Is this part compatible with my WDT780SAEM1 model"
# question = "How can I install part number PS11752778"

def backend_test_llm(question):
    # the query is the input to chatgpt asking it to find the most important keyword in a user provided question
    query = "in the response, only give me the most important noun phrase or part number or model number from in this sentence: " + question + ", no other words needed"

    ###### STEP 1: find the most relevant webpage using the keyword in user's question ######
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        ]

    # Add each new message to the list
    messages.append({"role": "user", "content": query})

    # Request gpt-3.5-turbo for chat completion
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages)

    # Print the response and add it to the messages list
    keyword = response.choices[0].message.content

    # this is the partselect url that searches for the webpage with most relevant info of the searchterm
    website_address = ("https://www.partselect.com/api/search/?searchterm=" + keyword).replace(" ", "%20")

    ###### STEP 2: find the top 10 most relevant urls on the webpage and load their text content ######
    
    # extract all urls from the website_address
    full_url_str = extract_url_from_page(website_address)
    
    # call chatgpt again to ask it pick the top 10 most relevant url to the question asked
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": full_url_str + \
                                "pick the top 10 most relevant url to the question: " + \
                                question +\
                                "format them in a string of urls separated with comma "}])
    picked_url = response.choices[0].message.content
    
    url_list = picked_url.split(",")
    doc_str = ""
    for url in url_list:
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        # get content in the main class container
        main_class = soup.find('main', class_='container')
        if main_class:
            text = main_class.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            doc_str += text + "\n"

    # initialize the langchain text splitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0, separator=' ')
    
    # create documents from the doc string, and split them it into chunks
    documents = text_splitter.create_documents([doc_str])

    # embed each chunk and with OpenAI embedding
    llm = OpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])

    # use qa chain to get the result that is the best answer to the question, return with the confidence score
    chain = load_qa_chain(llm, chain_type="map_rerank", verbose=True, return_intermediate_steps=True)
    try:
        result = chain({"input_documents": documents, "question": question}, return_only_outputs=True)
    except Exception as e:
        result = str(e)
        if result.startswith("Could not parse output: "):
            result = result.removeprefix("Could not parse output: ")
        return result
    return result['output_text']
    

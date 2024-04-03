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
from backend_crawler import main as crawler
# question = "Is this part compatible with my WDT780SAEM1 model"
# question = "How can I install part number PS11752778"
# question = "The ice maker on my Whirlpool fridge is not working. How can I fix it?"

def backend_answer_llm(question):
    query = "in the response, only give me the most important noun phrase or part number or model number from in this sentence: " + question + ", no other words needed"

    # How can I install part number PS11752778
    # Load your API key from an environment variable or secret management service

    RUN_CHATGPT = True

    if RUN_CHATGPT:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            ]
        # Add each new message to the list
        messages.append({"role": "user", "content": query})
        # Request gpt-3.5-turbo for chat completion
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=messages)

        # Print the response and add it to the messages list
        chat_message = response.choices[0].message.content
    else:
        chat_message = "WDT780SAEM1 model"

    print(f"extracted search info is", chat_message)
    website_address = ("https://www.partselect.com/api/search/?searchterm=" + chat_message).replace(" ", "%20")

    full_url_str = extract_url_from_page(website_address)
    # print("main_div", main_div)
    # Request gpt-3.5-turbo for chat completion
    if RUN_CHATGPT:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_url_str + \
                                    "pick the top 10 most relevant url to the question: " + \
                                    question +\
                                    "format them in a string of urls separated with comma "}])
        picked_url = response.choices[0].message.content
    else:
        picked_url = "https://www.partselect.com/Models/WDT780SAEM1/Parts/, https://www.partselect.com/Models/WDT780SAEM/Videos/, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=pZO1rcMwKBc, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=siE-8HethWg, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=fz1YHu782Wk, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=CQ6N_1G2zzE, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=3no3S5XCunU, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=X7SLvFAiTkw, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=X02l3pHeOUI, https://www.partselect.com/Models/WDT780SAEM/Videos/?VideoID=xJ3IgOnKoww, https://www.partselect.com/Models/WDT780SAEM/Instructions/, https://www.partselect.com/Models/WDT780SAEM/Instructions/, https://www.partselect.com/Repair/Dishwasher/, https://www.partselect.com/Repair/Dryer/, https://www.partselect.com/Repair/Microwave/, https://www.partselect.com/Repair/Range-Stove-Oven/, https://www.partselect.com/Repair/Refrigerator/, https://www.partselect.com/Repair/Washer/, https://www.partselect.com/Same-Day-Shipping.htm"
    print("picked_url", picked_url)

    url_list = picked_url.split(",")
    doc_str = ""
    for url in url_list:
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
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
        # f = open("demofile3.txt", "w")
        # f.write("Woops! I have deleted the content!")
        # f.close()
        # print(text)
        # cd
    # # Load the document, split it into chunks, embed each chunk and load it into the vector store.
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0, separator=' ')
    documents = text_splitter.create_documents([doc_str])
    llm = OpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])
    chain = load_qa_chain(llm, chain_type="map_rerank", verbose=True, return_intermediate_steps=True)
    try:
        result = chain({"input_documents": documents, "question": question}, return_only_outputs=True)
    except Exception as e:
        result = str(e)
        if result.startswith("Could not parse output: "):
            result = result.removeprefix("Could not parse output: ")
    print("result is ", result)
    return result

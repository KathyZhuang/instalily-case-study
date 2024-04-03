import os
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

from langchain.chains.question_answering import load_qa_chain
from langchain import OpenAI
os.environ["OPENAI_API_KEY"] = "OPEN_AI_KEY"
# Specify the root directory where you want to search for PDF files
root_directory = "/Users/kathy/instalily/case-study/output/www.partselect.com_1"
# Set the batch size (number of files to process in each batch)
batch_size = 100

# Initialize an empty list to store loaded documents
docs = []

# Function to process a batch of PDF files
# def process_pdf_batch(pdf_files):
#     batch_docs = []
#     for pdf_file_path in pdf_files:
#         pdf_loader = TextLoader(pdf_file_path)
#         batch_docs.extend(pdf_loader.load())
#     return batch_docs

# # Get the list of PDF files to process
# pdf_files_to_process = []
# for root, dirs, files in os.walk(root_directory):
#     pdf_files_to_process.extend([os.path.join(root, file) for file in files if file.lower().endswith(".txt")])
# # Create a ThreadPoolExecutor for parallel processing
# with ThreadPoolExecutor() as executor:
#     total_files = len(pdf_files_to_process)
#     processed_files = 0

#     # Iterate through the PDF files in batches
#     for i in range(0, total_files, batch_size):
#         batch = pdf_files_to_process[i:i+batch_size]
#         batch_docs = list(executor.map(process_pdf_batch, [batch]))
#         for batch_result in batch_docs:
#             docs.extend(batch_result)
#             processed_files += len(batch)
#             print(f"Processed {processed_files} / {total_files} files")
# print("docs", docs)
text_path = "/Users/kathy/instalily/case-study/model_txt.txt"
f = open(text_path, "r")
doc_string = f.read()

text_loader = TextLoader(text_path)
docs = text_loader.load()
# print(len(docs[0].page_content))
# print(doc_string)
# # Load the document, split it into chunks, embed each chunk and load it into the vector store.
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0, separator=' ')
documents = text_splitter.create_documents([doc_string])
llm = OpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])
chain = load_qa_chain(llm, chain_type="map_rerank", verbose=True, return_intermediate_steps=True)
query = "What is compatible with my WDT780SAEM1 model"
try:
    result = chain({"input_documents": documents, "question": query}, return_only_outputs=True)
except Exception as e:
    result = str(e)
    if result.startswith("Could not parse output: "):
        result = result.removeprefix("Could not parse output: ")
print("result is ", result)



# print(text_splitter.create_documents([doc_string]))
# print(len(documents[0].page_content))
# db = Chroma.from_documents(documents, OpenAIEmbeddings(),persist_directory="./chroma_db_5")
# query = "Which part is compatible with my WDT780SAEM1 model"
# docs = db.similarity_search(query)

# print("directly response_docs", docs[0].page_content)

# save to disk
# db.persist()


# query = "Which part is compatible with my WDT780SAEM1 model"
# db_load = Chroma(persist_directory="./chroma_db_5",embedding_function=OpenAIEmbeddings())
# response_docs = db_load.similarity_search(query)

# print("directly response_docs", response_docs[0].page_content)




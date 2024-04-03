from langchain.document_loaders.base import Document
from langchain.indexes import VectorstoreIndexCreator
from langchain.utilities import ApifyWrapper
import os

# Set up your Apify API token and OpenAI API key
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
os.environ["APIFY_API_TOKEN"] = "OPENAI_API_KEY"

apify = ApifyWrapper()

# Run the Website Content Crawler on a website, wait for it to finish, and save
# its results into a LangChain document loader:
print("after apify", apify)
loader = apify.call_actor(
    actor_id="apify/website-content-crawler",
    run_input={"startUrls": [{"url": "https://docs.apify.com/"}]},
    dataset_mapping_function=lambda item: Document(
        page_content=item["text"] or "", metadata={"source": item["url"]}
    ),
)
print("before index")
# Initialize the vector database with the text documents:
index = VectorstoreIndexCreator().from_loaders([loader])
print("done index")
# Finally, query the vector database:
query = "What is Apify?"
result = index.query_with_sources(query)
print(result["answer"])
print(result["sources"])

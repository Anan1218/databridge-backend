from googleapiclient.discovery import build
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import os
from dotenv import load_dotenv

load_dotenv()

def get_search_results(query: str, num_results: int = 10):
    service = build("customsearch", "v1", developerKey=os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"))
    
    try:
        results = service.cse().list(
            q=query,
            cx=os.getenv("GOOGLE_CSE_ID"),
            num=num_results
        ).execute()
        
        return results.get("items", [])
    except Exception as e:
        raise Exception(f"Error fetching search results: {str(e)}")

def process_search_results(results, llm):
    # Combine all snippets and content
    combined_text = ""
    for result in results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        combined_text += f"\nTitle: {title}\nSnippet: {snippet}\n"
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_text(combined_text)
    docs = [Document(page_content=t) for t in texts]
    
    # Summarize using Langchain
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.run(docs)
    
    return summary 
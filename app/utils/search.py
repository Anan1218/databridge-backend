import os
from typing import List, Tuple, Optional, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import asyncio

# Load environment variables
load_dotenv()

# Get API credentials from environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

async def perform_google_search(query: str, num_results: int = 10) -> List[str]:
    """
    Perform a Google search using the Custom Search JSON API
    """
    try:
        # Create a service object for the Custom Search API
        service = build('customsearch', 'v1', developerKey=GOOGLE_API_KEY)
        
        # Print debug information
        print(f"Searching for query: {query}")
        
        # Perform the search
        result = service.cse().list(
            q=query,
            cx='017576662512468239146:omuauf_lfve',
            num=num_results
        ).execute()
        
        # Extract and process results
        search_results = []
        if 'items' in result:
            for item in result['items']:
                content = f"Title: {item['title']}\nURL: {item['link']}\nDescription: {item.get('snippet', '')}\n"
                search_results.append(content)
            print(f"Found {len(search_results)} results")
        else:
            print("No items found in search results")
            print(f"Response: {result}")
        
        return search_results
    
    except HttpError as e:
        print(f"HTTP Error performing Google search: {e.resp.status} - {e.content}")
        return []
    except Exception as e:
        print(f"Error performing Google search: {str(e)}")
        return []

async def process_search_results(search_results: List[str]) -> Tuple[List[str], Optional[FAISS]]:
    """
    Process search results using LangChain and create vector embeddings
    """
    try:
        # Process results with LangChain
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_text('\n'.join(search_results))
        
        # Create vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts, embeddings)
        
        return texts, vectorstore
    except Exception as e:
        print(f"Error processing search results: {str(e)}")
        return [], None
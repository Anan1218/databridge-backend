from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List
import aiohttp
from bs4 import BeautifulSoup

async def fetch_url_content(url: str) -> str:
    """Fetch and extract text content from a URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(strip=True)

async def generate_report_content(search_queries: List[str], urls: List[str]) -> str:
    """Generate a comprehensive report using LangChain."""
    
    # Fetch content from all URLs
    url_contents = []
    for url in urls:
        try:
            content = await fetch_url_content(url)
            url_contents.append(content)
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            continue

    # Create prompt template
    prompt_template = """
    Based on the following search queries and content from various URLs, generate a comprehensive report.
    
    Search Queries:
    {queries}
    
    Content from URLs:
    {url_contents}
    
    Please create a detailed report that:
    1. Summarizes the main findings
    2. Identifies key patterns and insights
    3. Provides relevant recommendations
    4. Cites specific sources when appropriate
    
    Report:
    """

    prompt = PromptTemplate(
        input_variables=["queries", "url_contents"],
        template=prompt_template
    )

    # Initialize LangChain with ChatGPT
    llm = ChatOpenAI(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)

    # Generate report
    report = await chain.arun(
        queries="\n".join(search_queries),
        url_contents="\n\n".join(url_contents)
    )

    return report 
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List
from app.utils.search import perform_google_search, process_search_results

async def generate_report_content(search_queries: List[str], urls: List[str]) -> str:
    """Generate a comprehensive report using LangChain and search results."""
    
    # Collect search results using existing search functionality
    all_results = []
    for query in search_queries:
        search_results = await perform_google_search(query)
        texts, vectorstore = await process_search_results(search_results)
        all_results.extend(texts)

    # Create prompt template
    prompt_template = """
    Based on the following search queries and content, generate a comprehensive report.
    
    Search Queries:
    {queries}
    
    Content:
    {content}
    
    Please create a detailed report that:
    1. Summarizes the main findings
    2. Identifies key patterns and insights
    3. Provides relevant recommendations
    4. Cites specific sources when appropriate
    
    Report:
    """

    prompt = PromptTemplate(
        input_variables=["queries", "content"],
        template=prompt_template
    )

    # Initialize LangChain with ChatGPT
    llm = ChatOpenAI(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)

    # Generate report
    report = await chain.arun(
        queries="\n".join(search_queries),
        content="\n\n".join(all_results)
    )

    return report 
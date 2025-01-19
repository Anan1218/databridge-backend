from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List
from app.utils.search import perform_google_search, process_search_results
from app.utils.local_events import search_local_events, summarize_local_events

async def generate_report_content(search_queries: List[str], urls: List[str], location: str = None, businessName: str = None) -> dict:
    """Generate a comprehensive report using LangChain and include local events if location is provided."""
    
    # Collect search results using existing search functionality
    all_results = []
    for query in search_queries:
        search_results = await perform_google_search(query)
        texts, vectorstore = await process_search_results(search_results)
        all_results.extend(texts)

    # Create prompt template for main report
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

    If you can't find any information, just give a blank report.
    
    Report:
    """

    prompt = PromptTemplate(
        input_variables=["queries", "content"],
        template=prompt_template
    )

    # Initialize LangChain with ChatGPT
    llm = ChatOpenAI(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)

    # Generate main report
    main_report = await chain.arun(
        queries="\n".join(search_queries),
        content="\n\n".join(all_results)
    )

    # Initialize report structure
    report_data = {
        'main_content': main_report,
        'events': []
    }

    # If location is provided, search for local events
    if location:
        try:
            # Search for events in the area
            events = await search_local_events(
                location=location,
                date_range="upcoming"  # You can make this configurable if needed
            )
            
            # Add events to the report data
            report_data['events'] = events
            
            # Generate events summary
            events_summary = await summarize_local_events(events)
            report_data['events_summary'] = events_summary
            
        except Exception as e:
            print(f"Error fetching local events: {str(e)}")
            report_data['events_error'] = str(e)

    return report_data 
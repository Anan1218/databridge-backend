import os
from typing import List, Dict
from datetime import datetime
from app.utils.search import perform_google_search, process_search_results
from app.utils.address_parser import extract_city_and_state

async def search_local_events(location: str, event_type: str = None, date_range: str = None) -> List[Dict]:
    """
    Search for local events in a specific area with optional filters
    
    Args:
        location (str): The city or area to search for events
        event_type (str, optional): Type of event (e.g., "music", "sports", "art")
        date_range (str, optional): Time frame (e.g., "this weekend", "next month")
    """

    try:
        city, state = extract_city_and_state(location)
        # Construct search query
        base_query = f"events in {location}"
        if event_type:
            base_query += f" {event_type}"
        if date_range:
            base_query += f" {date_range}"
            
        # Add specific terms to improve event-related results
        search_query = f"{base_query} schedule dates tickets"
        
        # Perform the search
        search_results = await perform_google_search(search_query, num_results=15)
        
        # Process and structure the events
        events = []
        for result in search_results:
            # Parse the search result into structured event data
            event = parse_event_from_result(result)
            if event:
                events.append(event)
        
        return events
    
    except Exception as e:
        print(f"Error searching for local events: {str(e)}")
        return []

def parse_event_from_result(result: str) -> Dict:
    """
    Parse a search result into structured event data
    """
    try:
        # Split the result into components (Title, URL, Description)
        lines = result.split('\n')
        title = ""
        url = ""
        description = ""
        
        for line in lines:
            if line.startswith("Title: "):
                title = line.replace("Title: ", "")
            elif line.startswith("URL: "):
                url = line.replace("URL: ", "")
            elif line.startswith("Description: "):
                description = line.replace("Description: ", "")
        
        # Extract potential date and location from title/description
        event_data = {
            "title": title,
            "url": url,
            "description": description,
            "source": "Google Search",
            "extracted_date": extract_date(title + " " + description),
            "extracted_location": extract_location(title + " " + description)
        }
        
        return event_data
    
    except Exception as e:
        print(f"Error parsing event result: {str(e)}")
        return None

def extract_date(text: str) -> str:
    """
    Extract potential date information from text
    Basic implementation - can be enhanced with more sophisticated date parsing
    """
    # List of date-related keywords to look for
    date_keywords = [
        "today", "tomorrow", "tonight",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    
    # Find the first instance of a date keyword
    text_lower = text.lower()
    for keyword in date_keywords:
        if keyword in text_lower:
            # Find the surrounding context
            start = max(0, text_lower.find(keyword) - 20)
            end = min(len(text), text_lower.find(keyword) + 30)
            return text[start:end].strip()
    
    return ""

def extract_location(text: str) -> str:
    """
    Extract potential venue or location information from text
    Basic implementation - can be enhanced with NLP
    """
    # Look for location indicators
    location_indicators = ["at ", "in ", "venue: ", "location: "]
    text_lower = text.lower()
    
    for indicator in location_indicators:
        if indicator in text_lower:
            # Find the surrounding context
            start = text_lower.find(indicator) + len(indicator)
            end = min(len(text), start + 50)
            # Try to find a natural end to the location
            for delimiter in [",", ".", "\n"]:
                natural_end = text[start:end].find(delimiter)
                if natural_end != -1:
                    end = start + natural_end
                    break
            return text[start:end].strip()
    
    return ""

async def summarize_local_events(events: List[Dict]) -> str:
    """
    Generate a summary of local events
    """
    if not events:
        return "No events found."
    
    summary = "Here are the upcoming events in your area:\n\n"
    
    for i, event in enumerate(events, 1):
        summary += f"{i}. {event['title']}\n"
        if event['extracted_date']:
            summary += f"   When: {event['extracted_date']}\n"
        if event['extracted_location']:
            summary += f"   Where: {event['extracted_location']}\n"
        summary += f"   More info: {event['url']}\n\n"
    
    return summary 
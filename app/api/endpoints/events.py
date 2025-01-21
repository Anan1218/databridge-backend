from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from app.utils.firebase import db
from app.api.dependencies import verify_token
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
from datetime import datetime, date, timedelta
import calendar
from app.utils.address_parser import extract_city_and_state
import usaddress

router = APIRouter(
    tags=["events"]
)

# Pydantic models
class TicketmasterEvent(BaseModel):
    event_id: str
    name: str
    description: Optional[str]
    start_date: str
    end_date: Optional[str]
    url: str
    venue: Optional[dict]
    price_ranges: Optional[List[dict]]
    images: Optional[List[dict]]
    classifications: Optional[List[dict]]

class EventResponse(BaseModel):
    success: bool
    message: str
    events_count: Optional[int] = None
    error: Optional[str] = None

class EventRequest(BaseModel):
    location: str

async def fetch_ticketmaster_events(location: str) -> List[dict]:
    """Fetch events from Ticketmaster API"""
    api_key = os.getenv('TICKETMASTER_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Ticketmaster API key not configured")

    # Extract postal code from the full address and log it
    tagged_address, _ = usaddress.tag(location)
    postal_code = tagged_address.get('ZipCode')
    
    if not postal_code:
        raise HTTPException(status_code=400, detail="Could not find postal code in address. Please provide a valid address with ZIP code.")
    else:
        print(f"Extracted postal code: {postal_code}")

    # Get date range (today + 30 days)
    today = date.today()
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)

    # Format dates to the required format without milliseconds
    start_time = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    url = 'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'apikey': api_key,
        'postalCode': postal_code,
        'startDateTime': start_time,
        'endDateTime': end_time,
        'radius': 100,
        'unit': 'miles',
        'size': 100,
        'locale': '*'  # Include locale parameter as per your example
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if '_embedded' not in data or 'events' not in data['_embedded']:
            print("No events found in the response.")
            return []
            
        return data['_embedded']['events']
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@router.post("/events/{user_id}", response_model=EventResponse)
async def get_events(
    user_id: str,
    request: EventRequest
):
    try:
        # Fetch events from Ticketmaster and log the number of events
        events = await fetch_ticketmaster_events(request.location)
        print(f"Number of events fetched: {len(events)}")
        
        if not events:
            return {
                'success': True,
                'message': 'No events found for the specified criteria',
                'events_count': 0
            }
        
        # Get current month and year for collection name
        today = date.today()
        collection_id = f"{today.year}_{today.month:02d}"
        
        # Store events in Firebase
        events_ref = (db.collection('users')
                     .document(user_id)
                     .collection('events')
                     .document(collection_id)
                     .collection('event_items'))
        
        batch = db.batch()
        
        # Create metadata document
        month_metadata_ref = (db.collection('users')
                            .document(user_id)
                            .collection('events')
                            .document(collection_id))
        
        metadata = {
            'month': today.month,
            'year': today.year,
            'total_events': len(events),
            'location': request.location,
            'last_updated': firestore.SERVER_TIMESTAMP
        }
        batch.set(month_metadata_ref, metadata)
        
        for event in events:
            print(f"Processing event: {event['id']}")  # Log each event being processed
            event_doc = events_ref.document(event['id'])
            event_data = {
                'event_id': event['id'],
                'name': event['name'],
                'description': event.get('description', ''),
                'start_date': event['dates']['start'].get('dateTime'),
                'end_date': event['dates']['end'].get('dateTime') if 'end' in event['dates'] else None,
                'url': event.get('url', ''),
                'venue': event.get('_embedded', {}).get('venues', [{}])[0],
                'price_ranges': event.get('priceRanges', []),
                'images': event.get('images', []),
                'classifications': event.get('classifications', []),
                'created_at': firestore.SERVER_TIMESTAMP
            }
            print(f"Event data to be stored: {event_data}")  # Log the event data
            batch.set(event_doc, event_data)

        batch.commit()
        print("Batch commit successful.")  # Log successful commit

        return {
            'success': True,
            'message': f'Events successfully synced for {collection_id}',
            'events_count': len(events)
        }

    except Exception as e:
        print(f"Error during event sync: {str(e)}")  # Log the error
        return {
            'success': False,
            'message': 'Failed to sync events',
            'error': str(e)
        }

from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from app.utils.firebase import db
from app.api.dependencies import verify_token
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
from datetime import datetime, date
import calendar
import logging
from app.utils.address_parser import extract_city_and_state
import usaddress

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    # Extract postal code from the full address
    tagged_address, _ = usaddress.tag(location)
    postal_code = tagged_address.get('ZipCode')
    
    if not postal_code:
        raise HTTPException(status_code=400, detail="Could not find postal code in address. Please provide a valid address with ZIP code.")

    # Get current month date range
    today = date.today()
    _, last_day = calendar.monthrange(today.year, today.month)
    start_date = datetime(today.year, today.month, 1).isoformat() + 'Z'
    end_date = datetime(today.year, today.month, last_day).isoformat() + 'Z'

    url = 'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'apikey': api_key,
        'postalCode': postal_code,  # Changed from city/state to postal code
        'startDateTime': start_date,
        'endDateTime': end_date,
        'radius': 15,
        'unit': 'miles',
        'size': 100  # Maximum number of results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Check if events exist in response
        if '_embedded' not in data or 'events' not in data['_embedded']:
            return []
            
        return data['_embedded']['events']
    except requests.exceptions.RequestException as e:
        logger.error(f"Ticketmaster API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@router.post("/events/{user_id}", response_model=EventResponse)
async def get_events(
    user_id: str,
    request: EventRequest
):
    try:
        # Fetch events from Ticketmaster
        events = await fetch_ticketmaster_events(request.location)
        
        # Store events in Firebase
        events_ref = db.collection('users').document(user_id).collection('events')
        batch = db.batch()
        
        for event in events:
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
            batch.set(event_doc, event_data)

        # Commit the batch
        batch.commit()

        return {
            'success': True,
            'message': 'Events successfully synced',
            'events_count': len(events)
        }

    except Exception as e:
        logger.error(f"Error syncing events: {str(e)}")
        return {
            'success': False,
            'message': 'Failed to sync events',
            'error': str(e)
        }

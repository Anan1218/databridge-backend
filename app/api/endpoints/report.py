from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
from app.utils.firebase import db
from pydantic import BaseModel
from typing import List, Optional
from app.services.report_service import generate_report_content

router = APIRouter()

class ReportRequest(BaseModel):
    email: str
    userId: str
    searchQueries: List[str]
    urls: List[str]
    location: Optional[str] = None  # Added location field
    businessName: Optional[str] = None  # Added businessName field
    reportId: Optional[str] = None  # Add this field

class ReportResponse(BaseModel):
    success: bool
    reportId: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    try:
        # Generate report content using LangChain
        report_content = await generate_report_content(
            search_queries=request.searchQueries,
            urls=request.urls,
            location=request.location,
            business_name=request.businessName
        )
        
        # Create a new report document
        report_ref = db.collection('users').document(request.userId)\
                      .collection('reports').document()
        
        # Create document with minimal data
        report_data = {
            'userId': request.userId,
            'email': request.email,
            'status': 'completed',
            'content': report_content['main_content'],
            'timestamp': firestore.SERVER_TIMESTAMP,
        }
        
        # Add events summary if available
        if 'events_summary' in report_content:
            report_data['events_summary'] = report_content['events_summary']
            
        # Create the document
        report_ref.set(report_data)
        
        # Store events in subcollection if they exist
        if report_content.get('events'):
            events_collection = report_ref.collection('events')
            for event in report_content['events']:
                event_data = {
                    'name': event.get('name'),
                    'description': event.get('description'),
                    'date': event.get('date'),
                    'location': event.get('location'),
                    'url': event.get('url'),
                    'timestamp': firestore.SERVER_TIMESTAMP
                }
                events_collection.add(event_data)
        
        return {
            'success': True,
            'reportId': report_ref.id
        }
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        } 
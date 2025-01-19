from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
from app.utils.firebase import db
from pydantic import BaseModel
from typing import List, Optional
from app.services.report_service import generate_report_content
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info("=== ENDPOINT CALLED ===")
        logger.info(f"Received request: {request}")
        
        # Debug logs
        logger.info("================================================")
        logger.info(f"Search Queries: {request.searchQueries}")
        logger.info(f"URLs: {request.urls}")
        logger.info(f"Location: {request.location}")
        logger.info(f"Business Name: {request.businessName}")
        logger.info(f"User ID: {request.userId}")
        logger.info(f"Email: {request.email}")
        
        # Generate report content using LangChain
        logger.info("=== GENERATING REPORT CONTENT ===")
        report_content = await generate_report_content(
            search_queries=request.searchQueries,
            urls=request.urls,
            location=request.location,
            businessName=request.businessName
        )
        logger.info(f"Report content generated: {report_content}")
        
        # Create a new report document
        logger.info("=== CREATING FIREBASE DOCUMENT ===")
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
        logger.info(f"Saving document with data: {report_data}")
        report_ref.set(report_data)
        logger.info(f"Document saved with ID: {report_ref.id}")
        
        # Store events in subcollection if they exist
        if report_content.get('events'):
            logger.info("=== STORING EVENTS ===")
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
            logger.info(f"Stored {len(report_content['events'])} events")
        
        logger.info("=== ENDPOINT COMPLETED SUCCESSFULLY ===")
        return {
            'success': True,
            'reportId': report_ref.id
        }
        
    except Exception as e:
        logger.error("=== ERROR IN ENDPOINT ===")
        logger.error(f"Error generating report: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        } 
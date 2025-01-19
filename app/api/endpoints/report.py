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
            business_name=request.businessName  # Pass businessName to report generator
        )
        
        # Create a new report document under the user's reports collection
        user_ref = db.collection('users').document(request.userId)
        reports_ref = user_ref.collection('reports').document()
        
        # Store main report data
        report_data = {
            'userId': request.userId,
            'email': request.email,
            'searchQueries': request.searchQueries,
            'urls': request.urls,
            'location': request.location,
            'businessName': request.businessName,  # Added businessName to stored data
            'status': 'completed',
            'content': report_content['main_content'],
            'timestamp': firestore.SERVER_TIMESTAMP,
        }
        
        # Create the main report document
        reports_ref.set(report_data)
        
        # If events were found, store them in a subcollection
        if report_content.get('events'):
            events_collection = reports_ref.collection('events')
            for event in report_content['events']:
                events_collection.add({
                    **event,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
        
        return ReportResponse(
            success=True,
            reportId=reports_ref.id
        )
        
    except Exception as e:
        return ReportResponse(
            success=False,
            error=str(e)
        ) 
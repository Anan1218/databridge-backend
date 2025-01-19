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
            urls=request.urls
        )
        
        # Create a new report document under the user's reports collection
        user_ref = db.collection('users').document(request.userId)
        reports_ref = user_ref.collection('reports').document()
        
        report_data = {
            'userId': request.userId,
            'email': request.email,
            'searchQueries': request.searchQueries,
            'urls': request.urls,
            'status': 'completed',
            'content': report_content,
            'timestamp': firestore.SERVER_TIMESTAMP,
        }
        reports_ref.set(report_data)
        
        return ReportResponse(
            success=True,
            reportId=reports_ref.id
        )
        
    except Exception as e:
        return ReportResponse(
            success=False,
            error=str(e)
        ) 
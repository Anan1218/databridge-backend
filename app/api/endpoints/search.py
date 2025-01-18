from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from app.utils.firebase import db
from app.api.dependencies import verify_token
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
async def generate_report(request: ReportRequest, token = Depends(verify_token)):
    try:
        # Verify if the token matches the userId for additional security
        if token.get('uid') != request.userId:
            raise HTTPException(status_code=403, detail="Unauthorized access")
            
        # Generate report content using LangChain
        report_content = await generate_report_content(
            search_queries=request.searchQueries,
            urls=request.urls
        )
        
        # Create a new report document in Firebase
        report_ref = db.collection('reports').document()
        report_data = {
            'userId': request.userId,
            'email': request.email,
            'searchQueries': request.searchQueries,
            'urls': request.urls,
            'status': 'completed',
            'content': report_content,
            'timestamp': firestore.SERVER_TIMESTAMP,
        }
        report_ref.set(report_data)
        
        return ReportResponse(
            success=True,
            reportId=report_ref.id
        )
        
    except Exception as e:
        return ReportResponse(
            success=False,
            error=str(e)
        ) 
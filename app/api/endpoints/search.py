from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from app.utils.firebase import db
from app.utils.search import perform_google_search, process_search_results, batch_search_and_process
from app.api.dependencies import verify_token
from pydantic import BaseModel
from typing import List, Optional
from app.services.report_service import generate_report_content

router = APIRouter()

class SearchRequest(BaseModel):
    queries: List[str]
    num_results: Optional[int] = 10

class BatchSearchRequest(BaseModel):
    queries: List[str]
    num_results_per_query: Optional[int] = 10

class SearchResponse(BaseModel):
    raw_results: List[str]
    processed_chunks: List[str]
    success: bool
    error: Optional[str] = None

class ReportRequest(BaseModel):
    email: str
    userId: str
    searchQueries: List[str]
    urls: List[str]

class ReportResponse(BaseModel):
    success: bool
    reportId: Optional[str] = None
    error: Optional[str] = None

@router.post("/search")
async def search_and_summarize(request: SearchRequest, token = Depends(verify_token)):
    try:
        user_id = token.get('uid')
        results = []
        for query in request.queries:
            # Get search results
            search_results = await perform_google_search(query, request.num_results)
            
            # Process and summarize results
            summary = process_search_results(search_results)
            
            # Store in Firebase
            doc_ref = db.collection('searches').document()
            doc_data = {
                'userId': user_id,
                'query': query,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'rawResults': search_results,
                'summary': summary
            }
            doc_ref.set(doc_data)
            
            results.append({
                'query': query,
                'summary': summary,
                'searchId': doc_ref.id
            })
        
        return {
            'success': True,
            'results': results
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/searches")
async def get_searches(token = Depends(verify_token)):
    try:
        user_id = token.get('uid')
        searches_ref = db.collection('searches')
        
        searches = []
        for doc in searches_ref.stream():
            data = doc.to_dict()
            searches.append({
                'id': doc.id,
                'query': data.get('query'),
                'summary': data.get('summary'),
                'timestamp': data.get('timestamp')
            })
            
        return searches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/batch", response_model=SearchResponse)
async def batch_search(request: BatchSearchRequest, token: str = Depends(verify_token)):
    try:
        raw_results, processed_texts, vectorstore = await batch_search_and_process(
            request.queries,
            request.num_results_per_query
        )
        
        user_id = token['uid']
        results_ref = db.collection('users').document(user_id).collection('search_results')
        
        batch_ref = results_ref.add({
            'queries': request.queries,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'num_results': len(raw_results),
            'num_processed_chunks': len(processed_texts)
        })
        
        return SearchResponse(
            raw_results=raw_results,
            processed_chunks=processed_texts,
            success=True
        )
        
    except Exception as e:
        return SearchResponse(
            raw_results=[],
            processed_chunks=[],
            success=False,
            error=str(e)
        ) 

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
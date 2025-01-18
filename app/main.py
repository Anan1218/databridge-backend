from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth, firestore
from app.utils.firebase import db
from app.utils.search import perform_google_search, process_search_results
from pydantic import BaseModel
from typing import List, Optional
from langchain.llms import OpenAI

app = FastAPI(
    title="DataBridge API",
    description="Backend API for DataBridge application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    queries: List[str]
    num_results: Optional[int] = 10

# Firebase auth middleware
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/search")
async def search_and_summarize(request: SearchRequest, token = Depends(verify_token)):
    try:
        user_id = token.get('uid')
        llm = OpenAI(temperature=0)
        
        results = []
        for query in request.queries:
            # Get search results
            search_results = get_search_results(query, request.num_results)
            
            # Process and summarize results
            summary = process_search_results(search_results, llm)
            
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

@app.get("/api/searches")
async def get_searches(token = Depends(verify_token)):
    try:
        user_id = token.get('uid')
        searches_ref = db.collection('searches')
        query = searches_ref.where('userId', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING)
        
        searches = []
        for doc in query.stream():
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
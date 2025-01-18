from firebase_admin import firestore
from datetime import datetime, timedelta
import asyncio
from app.utils.firebase import db
from app.utils.search import search_and_process

# Commented out for temporary disable
"""
async def process_user_searches():
    # Get all users who need their searches updated
    users_ref = db.collection('users')
    week_ago = datetime.now() - timedelta(days=7)
    
    # Query for users who haven't been updated in a week
    users = users_ref.where('last_search_update', '<', week_ago).stream()
    
    for user in users:
        user_data = user.to_dict()
        await update_user_searches(user.id, user_data)

async def update_user_searches(user_id: str, user_data: dict):
    try:
        # Get user's search preferences
        search_terms = user_data.get('search_terms', [])
        
        # Process each search term
        for term in search_terms:
            # Perform search and process results
            search_results, texts, vectorstore = await search_and_process(term)
            
            # Store processed results in Firebase
            results_ref = db.collection('users').document(user_id).collection('search_results')
            
            # Store each chunk as a separate document
            for text in texts:
                results_ref.add({
                    'content': text,
                    'search_term': term,
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'search_batch': datetime.now().isoformat()
                })
        
        # Update user's last search timestamp
        db.collection('users').document(user_id).update({
            'last_search_update': firestore.SERVER_TIMESTAMP
        })
        
    except Exception as e:
        print(f"Error processing searches for user {user_id}: {str(e)}")
        # Log error to Firebase
        db.collection('errors').add({
            'user_id': user_id,
            'error': str(e),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
"""

def run_scheduler():
    """
    Temporarily disabled scheduler
    """
    print("Scheduler is temporarily disabled")
    pass 
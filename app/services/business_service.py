from firebase_admin import firestore
from app.utils.firebase import db
from app.utils.search import generate_business_report
from datetime import datetime

class BusinessService:
    def __init__(self):
        self.db = db

    async def create_or_update_business(self, user_id: str, business_data: dict) -> dict:
        """Create or update a business profile"""
        business_ref = self.db.collection('businesses').document(user_id)
        
        business_data['updated_at'] = firestore.SERVER_TIMESTAMP
        business_ref.set(business_data, merge=True)
        
        return business_data

    async def get_business_report(self, user_id: str) -> dict:
        """Get existing report or generate new one"""
        business_ref = self.db.collection('businesses').document(user_id)
        reports_ref = business_ref.collection('reports')
        
        # Check for today's report
        today = datetime.now().strftime('%Y-%m-%d')
        recent_report = reports_ref.where('date', '==', today).limit(1).stream()
        
        for report in recent_report:
            return report.to_dict()
        
        # No recent report - generate new one
        business_doc = business_ref.get()
        if not business_doc.exists:
            raise ValueError("Business not found")
            
        business_data = business_doc.to_dict()
        new_report = await generate_business_report(business_data)
        
        # Store report
        reports_ref.add({
            **new_report,
            'date': today
        })
        
        return new_report 
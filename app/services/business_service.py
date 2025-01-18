from firebase_admin import firestore
from app.utils.firebase import db
from app.utils.search import generate_business_insights
from datetime import datetime, timedelta
from typing import Optional, Dict

class BusinessService:
    def __init__(self):
        self.db = db

    async def create_or_update_business(self, user_id: str, business_data: dict) -> dict:
        """Create or update a business profile"""
        business_ref = self.db.collection('businesses').document(user_id)
        
        business_data['updated_at'] = firestore.SERVER_TIMESTAMP
        business_ref.set(business_data, merge=True)
        
        return business_data

    async def get_business_report(self, user_id: str) -> Optional[Dict]:
        """Get existing report or generate new one"""
        business_ref = self.db.collection('businesses').document(user_id)
        reports_ref = business_ref.collection('reports')
        
        # Check for valid report within the last week
        week_ago = datetime.now() - timedelta(days=7)
        recent_reports = reports_ref.where(
            'generated_at', '>', week_ago
        ).limit(1).stream()
        
        # Return existing report if found
        for report in recent_reports:
            return report.to_dict()
        
        # Generate new report if none exists or is expired
        return await self._generate_new_report(user_id, business_ref)

    async def _generate_new_report(self, user_id: str, business_ref) -> Dict:
        """Generate a new business report"""
        business_doc = business_ref.get()
        if not business_doc.exists:
            raise ValueError("Business not found")
            
        business_data = business_doc.to_dict()
        
        # Generate insights using search utility
        insights = await generate_business_insights(
            business_name=business_data['business_name'],
            location=business_data['location'],
            industry=business_data.get('industry')
        )
        
        # Create report
        now = datetime.now()
        report = {
            'local_competitors': insights['competitors'],
            'market_insights': insights['market_insights'],
            'trending_topics': insights['trends'],
            'generated_at': now,
            'valid_until': now + timedelta(days=7)
        }
        
        # Store report
        reports_ref = business_ref.collection('reports')
        reports_ref.add(report)
        
        return report 
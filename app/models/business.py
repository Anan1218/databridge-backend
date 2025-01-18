from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BusinessCreate(BaseModel):
    business_name: str
    location: str
    industry: Optional[str] = None
    website: Optional[str] = None

class BusinessReport(BaseModel):
    local_competitors: List[dict]
    market_insights: List[str]
    trending_topics: List[str]
    generated_at: datetime
    valid_until: datetime 
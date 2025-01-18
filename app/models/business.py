from pydantic import BaseModel
from typing import Optional

class Business(BaseModel):
    business_name: str
    location: str
    industry: Optional[str] = None
    website: Optional[str] = None

class BusinessReport(BaseModel):
    local_competitors: list
    market_insights: list
    trending_topics: list
    generated_at: str 
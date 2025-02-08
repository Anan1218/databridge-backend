from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class RedditPost(Base):
    __tablename__ = "reddit_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    subreddit = Column(String, index=True)
    score = Column(Integer)
    created_utc = Column(DateTime)
    content = Column(Text)
    inserted_at = Column(DateTime(timezone=True), server_default=func.now()) 
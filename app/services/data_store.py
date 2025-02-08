from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.reddit_post import RedditPost
from app.database import SessionLocal

reddit_posts: List[Dict] = []

def add_posts(posts_list: list, subreddit: str):
    db = SessionLocal()
    try:
        for post in posts_list:
            # Check if post already exists
            existing_post = db.query(RedditPost).filter(RedditPost.url == post["url"]).first()
            if not existing_post:
                db_post = RedditPost(
                    title=post["title"],
                    url=post["url"],
                    subreddit=subreddit,
                    score=post["score"],
                    created_utc=post["created_utc"],
                    content=post.get("content", ""),
                )
                db.add(db_post)
        db.commit()
    finally:
        db.close()

def get_all_posts():
    db = SessionLocal()
    try:
        return db.query(RedditPost).all()
    finally:
        db.close()

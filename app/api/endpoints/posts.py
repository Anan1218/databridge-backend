from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.data_store import get_all_posts

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/posts", tags=["posts"])
def list_posts(db: Session = Depends(get_db)):
    """
    Endpoint to list all posts from the datastore.
    """
    return get_all_posts(db) 
import pytest
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def load_env():
    """Load environment variables before each test"""
    load_dotenv()
    # Verify required environment variables are set
    required_vars = ['GOOGLE_API_KEY', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.skip(f"Missing required environment variables: {', '.join(missing_vars)}")

@pytest.fixture
def mock_search_results():
    """Sample search results for testing"""
    return [
        "Title: Test1\nURL: http://test1.com\nDescription: Description1",
        "Title: Test2\nURL: http://test2.com\nDescription: Description2"
    ] 
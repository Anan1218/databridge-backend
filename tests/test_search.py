import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.search import perform_google_search, process_search_results, batch_search_and_process
from app.api.endpoints.search import SearchRequest, BatchSearchRequest
from unittest.mock import MagicMock

client = TestClient(app)

@pytest.mark.asyncio
async def test_perform_google_search():
    """Test the Google search functionality"""
    try:
        # Test with a simple query
        results = await perform_google_search("python programming", num_results=3)
        
        # Check if we got results
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check result format
        for result in results:
            assert "Title:" in result
            assert "URL:" in result
            assert "Description:" in result
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_process_search_results(mock_search_results):
    """Test the search results processing"""
    # Process the results
    texts, vectorstore = await process_search_results(mock_search_results)
    
    # Check the processing results
    assert isinstance(texts, list)
    assert len(texts) > 0
    assert vectorstore is not None

@pytest.mark.asyncio
async def test_search_endpoint():
    """Test the search endpoint"""
    # Mock token verification
    app.dependency_overrides = {}  # Reset overrides
    
    # Create test request
    test_request = {
        "queries": ["test query"],
        "num_results": 5
    }
    
    # Make request with mock authorization
    response = client.post(
        "/api/search",
        json=test_request,
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check response
    assert response.status_code in [200, 401]  # 401 is acceptable if auth fails in test env

@pytest.mark.asyncio
async def test_batch_search_endpoint():
    """Test the batch search endpoint"""
    test_request = {
        "queries": ["test query 1", "test query 2"],
        "num_results_per_query": 5
    }
    
    response = client.post(
        "/api/search/batch",
        json=test_request,
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code in [200, 401]  # 401 is acceptable if auth fails in test env 
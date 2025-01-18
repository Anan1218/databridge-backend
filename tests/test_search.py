import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.search import perform_google_search, process_search_results, search_and_process, batch_search_and_process
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
async def test_search_and_process():
    """Test the combined search and process functionality"""
    # Perform search and processing
    search_results, texts, vectorstore = await search_and_process("python programming", num_results=2)
    
    # Check all components
    assert isinstance(search_results, list)
    assert len(search_results) > 0
    assert isinstance(texts, list)
    assert len(texts) > 0
    assert vectorstore is not None

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in search functions"""
    # Test with invalid API key
    import os
    original_key = os.getenv('GOOGLE_API_KEY')
    os.environ['GOOGLE_API_KEY'] = 'invalid_key'
    
    results = await perform_google_search("test")
    assert len(results) == 0  # Should return empty list on error
    
    # Restore original key
    if original_key:
        os.environ['GOOGLE_API_KEY'] = original_key 

@pytest.mark.asyncio
async def test_batch_search_and_process():
    """Test the batch search and process functionality"""
    # Test queries
    queries = ["python programming", "machine learning basics"]
    
    # Perform batch search and processing
    search_results, texts, vectorstore = await batch_search_and_process(queries, num_results=2)
    
    # Check components
    assert isinstance(search_results, list)
    assert len(search_results) > 0
    assert isinstance(texts, list)
    assert len(texts) > 0
    assert vectorstore is not None
    
    # Verify we got results for multiple queries
    assert any("python" in result.lower() for result in search_results)
    assert any("learning" in result.lower() for result in search_results)

@pytest.mark.asyncio
async def test_batch_search_api(client, monkeypatch):
    """Test the batch search API endpoint"""
    # Mock the batch_search_and_process function
    async def mock_batch_search(*args, **kwargs):
        return (
            ["Result 1", "Result 2"],
            ["Chunk 1", "Chunk 2"],
            MagicMock()  # Mock vectorstore
        )
    
    monkeypatch.setattr(
        "app.utils.search.batch_search_and_process",
        mock_batch_search
    )
    
    # Mock Firebase auth
    def mock_verify_token(token):
        return {"uid": "test_user"}
    
    monkeypatch.setattr(
        "app.main.verify_token",
        mock_verify_token
    )
    
    # Test request
    response = await client.post(
        "/api/search/batch",
        json={
            "queries": ["python", "machine learning"],
            "num_results_per_query": 5
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["raw_results"]) > 0
    assert len(data["processed_chunks"]) > 0 
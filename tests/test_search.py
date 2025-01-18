import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.search import perform_google_search, process_search_results, search_and_process

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
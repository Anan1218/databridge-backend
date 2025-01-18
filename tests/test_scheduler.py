# import pytest
# import asyncio
# from datetime import datetime, timedelta
# from unittest.mock import patch, MagicMock
# from app.utils.search_scheduler import process_user_searches, update_user_searches

# @pytest.mark.asyncio
# async def test_update_user_searches():
#     """Test updating searches for a single user"""
#     # Mock user data
#     user_id = "test_user_123"
#     user_data = {
#         "search_terms": ["python programming", "machine learning"]
#     }
    
#     # Mock Firebase references
#     mock_doc_ref = MagicMock()
#     mock_collection_ref = MagicMock()
#     mock_collection_ref.add = MagicMock()
#     mock_doc_ref.collection.return_value = mock_collection_ref
    
#     # Patch the necessary dependencies
#     with patch('app.utils.search_scheduler.db') as mock_db, \
#          patch('app.utils.search_scheduler.search_and_process') as mock_search:
        
#         # Setup mock return values
#         mock_db.collection().document.return_value = mock_doc_ref
#         mock_search.return_value = (
#             ["mock search result"],  # search_results
#             ["mock processed text"],  # texts
#             MagicMock()  # vectorstore
#         )
        
#         # Run the function
#         await update_user_searches(user_id, user_data)
        
#         # Verify the function made the expected calls
#         assert mock_search.call_count == len(user_data["search_terms"])
#         assert mock_collection_ref.add.call_count == len(user_data["search_terms"])
#         mock_doc_ref.update.assert_called_once()

# @pytest.mark.asyncio
# async def test_process_user_searches():
#     """Test processing searches for all users"""
#     # Mock user data
#     mock_users = [
#         MagicMock(id="user1", to_dict=lambda: {"search_terms": ["term1"]}),
#         MagicMock(id="user2", to_dict=lambda: {"search_terms": ["term2"]})
#     ]
    
#     # Patch the necessary dependencies
#     with patch('app.utils.search_scheduler.db') as mock_db, \
#          patch('app.utils.search_scheduler.update_user_searches') as mock_update:
        
#         # Setup mock return values
#         mock_db.collection().where().stream.return_value = mock_users
#         mock_update.return_value = None
        
#         # Run the function
#         await process_user_searches()
        
#         # Verify the function made the expected calls
#         assert mock_update.call_count == len(mock_users)

# @pytest.mark.asyncio
# async def test_error_handling_in_update():
#     """Test error handling in update_user_searches"""
#     # Mock user data
#     user_id = "test_user_error"
#     user_data = {
#         "search_terms": ["python programming"]
#     }
    
#     # Patch the dependencies to simulate an error
#     with patch('app.utils.search_scheduler.db') as mock_db, \
#          patch('app.utils.search_scheduler.search_and_process') as mock_search:
        
#         # Setup mock to raise an exception
#         mock_search.side_effect = Exception("Test error")
#         mock_errors_collection = MagicMock()
#         mock_db.collection.return_value = mock_errors_collection
        
#         # Run the function
#         await update_user_searches(user_id, user_data)
        
#         # Verify error was logged to Firebase
#         mock_errors_collection.add.assert_called_once() 
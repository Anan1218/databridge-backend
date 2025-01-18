from app.utils.firebase import db
from firebase_admin import firestore

def test_firebase_connection():
    try:
        # Try to access a collection
        test_collection = db.collection('test')
        
        # Try to add a document
        doc_ref = test_collection.add({
            'test_field': 'test_value',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print("✅ Successfully connected to Firebase and wrote to Firestore!")
        
        # Clean up - delete the test document
        doc_ref[1].delete()
        
    except Exception as e:
        print("❌ Firebase connection test failed:")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_firebase_connection() 
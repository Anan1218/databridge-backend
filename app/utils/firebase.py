import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase Admin with your service account
cred = credentials.Certificate("../../serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client() 
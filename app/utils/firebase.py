import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

# Initialize Firebase Admin with your service account
cred = credentials.Certificate("env/databridge-c1802-firebase-adminsdk-9gliq-535eb02d20.json")
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client() 
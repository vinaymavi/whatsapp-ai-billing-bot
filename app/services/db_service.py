import logging

import firebase_admin
from firebase_admin import firestore

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

DB_NAME = 'whatsapp-chatbot' 

class FirestoreService:    
    def __init__(self, cred_path: str = None):
        firebase_admin.initialize_app()
        self.db_app = firebase_admin.get_app()
        self.db = firestore.client(app=self.db_app,database_id=DB_NAME)
        
        self.users_collection = settings.firestore_collection_users
        self.bills_collection = settings.firestore_collection_bills
        self.transactions_collection = settings.firestore_collection_transactions

    def write(self, collection: str, document_id: str, data: dict):
        self.db.collection(collection).document(document_id).set(data)

    def read(self, collection: str, document_id: str):
        doc = self.db.collection(collection).document(document_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

db_service = FirestoreService()

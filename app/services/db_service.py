import logging
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import get_settings
from app.utils.constants import DEFAULT_PAGE_SIZE
from app.utils.helpers import get_ttl_key

logger = logging.getLogger(__name__)

DB_NAME = "whatsapp-chatbot"

setting = get_settings()


class FirestoreService:
    def __init__(self, cred_path: str = None):
        try:
            logger.info("DB service initialization started")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            self.db_app = firebase_admin.get_app()
            self.db = firestore.client(app=self.db_app, database_id=DB_NAME)
            logger.info("DB service initialized successfully.")
        except Exception as e:
            logger.error(f"Something went wrong {e}")

    def write(self, collection: str, document_id: str, data: Dict):
        try:
            self.db.collection(collection).document(document_id).set(data)
        except Exception as e:
            logger.error(f"Something went wrong {e}")

    def read(self, collection: str, document_id: str) -> Any | None:
        doc = self.db.collection(collection).document(document_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def read_list(
        self,
        collection: str,
        page: int,
        order_by: str,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> List[Any]:
        if page < 1:
            raise ValueError("Page must be >= 1")
        offset = (page - 1) * page_size
        docs = (
            self.db.collection(collection)
            .order_by(order_by)
            .limit(page_size)
            .offset(offset)
            .stream()
        )
        return [doc.to_dict() for doc in docs]

    def write_with_ttl(
        self,
        collection: str,
        document_id: str,
        data: Dict,
        ttl_seconds: Optional[int] = 300,
    ):
        _data = data | get_ttl_key(ttl_seconds=ttl_seconds)
        return self.write(collection, document_id, _data)

    def delete(self, collection: str, document_id: str):
        self.db.collection(collection).document(document_id).delete()


db_service = FirestoreService(setting.gcp_credentials_path)

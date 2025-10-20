import logging
import traceback
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
        self.db = None
        self.db_app = None
        self.initialization_error = None

        try:
            logger.info("DB service initialization started")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            self.db_app = firebase_admin.get_app()
            self.db = firestore.client(app=self.db_app, database_id=DB_NAME)
            logger.info("DB service initialized successfully.")
        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"Failed to initialize DB service: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

    def _check_db_initialized(self, operation: str) -> None:
        """Check if database is initialized, raise RuntimeError if not."""
        if self.db is None:
            logger.error(
                f"Cannot {operation} database: DB not initialized. "
                f"Initialization error: {self.initialization_error}"
            )
            raise RuntimeError(
                f"Firestore database is not initialized: {self.initialization_error}"
            )

    def write(self, collection: str, document_id: str, data: Dict):
        try:
            self._check_db_initialized("write to")
            self.db.collection(collection).document(document_id).set(data)
            logger.debug(
                f"Successfully wrote document {document_id} to collection {collection}"
            )
        except Exception as e:
            logger.error(f"Error writing to database: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def read(self, collection: str, document_id: str) -> Any | None:
        try:
            self._check_db_initialized("read from")
            doc = self.db.collection(collection).document(document_id).get()
            if doc.exists:
                logger.debug(
                    f"Successfully read document {document_id} from collection {collection}"
                )
                return doc.to_dict()
            logger.debug(f"Document {document_id} not found in collection {collection}")
            return None
        except Exception as e:
            logger.error(f"Error reading from database: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def read_list(
        self,
        collection: str,
        page: int,
        order_by: str,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> List[Any]:
        try:
            self._check_db_initialized("read from")
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
            result = [doc.to_dict() for doc in docs]
            logger.debug(
                f"Successfully read {len(result)} documents from collection {collection} (page {page})"
            )
            return result
        except Exception as e:
            logger.error(f"Error reading list from database: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

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
        try:
            self._check_db_initialized("delete from")
            self.db.collection(collection).document(document_id).delete()
            logger.debug(
                f"Successfully deleted document {document_id} from collection {collection}"
            )
        except Exception as e:
            logger.error(f"Error deleting from database: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


db_service = FirestoreService(setting.gcp_credentials_path)

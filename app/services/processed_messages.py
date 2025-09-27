from app.config import get_settings
from app.services.db_service import db_service
from app.utils.global_logging import get_logger

settings = get_settings()

logger = get_logger(__name__)


def check_message_status_and_save(message_id: str) -> bool:
    """
    Check the status of a message and save it to the database.
    Return True if message already processed else False

    Args:
        message_id (str): The ID of the message to check.
    """
    # Check the message status
    message = db_service.read(
        settings.firestore_collection_processed_messages, message_id
    )

    if message is not None:
        # Message already processed
        logger.warning(f"message with message_id={message_id} already processed")
        return True

    db_service.write_with_ttl(
        settings.firestore_collection_processed_messages,
        message_id,
        {"status": "processed"},
        ttl_seconds=3600,
    )

    return False

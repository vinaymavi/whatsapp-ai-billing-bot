from app.celery.celery_app import app
from app.services.gcp_storage import gcp_storage
from app.utils.background_job import WebDocumentJob, process_web_document
from app.utils.constants import CHUNK_SIZE
from app.utils.global_logging import get_logger

logger = get_logger("tasks")


@app.task
def process_file(gcs_path: str, file_type: str, user_id: str, doc_filename: str):
    """
    Celery task to process a file uploaded from the web application.

    Args:
        gcs_path: Path to the file in GCS
        file_type: MIME type of the document (e.g., 'application/pdf')
        user_id: ID of the user who uploaded the document
        doc_filename: Original filename of the document
    """
    logger.info(f"Starting file processing task - GCS_PATH: {gcs_path}")
    try:
        # Read the file from GCS and get temporary file path
        temp_filepath = gcp_storage.read_stream(gcs_path, CHUNK_SIZE)
        logger.info(f"temp_filepath = {temp_filepath}")

        # Create WebDocumentJob
        web_document = WebDocumentJob(
            user_id=user_id,
            doc_filename=doc_filename,
            doc_mime=file_type,
            gcs_path=gcs_path,
        )

        # Process the document
        process_web_document(web_document, gcs_path, temp_filepath)
        logger.info("File processed successfully")
    except Exception as e:
        logger.error(f"Error processing file {gcs_path}: {e}")

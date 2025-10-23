from app.celery.celery_app import app
from app.utils.global_logging import get_logger

logger = get_logger("tasks")


@app.task
def process_file(gcs_path: str, file_type: str):
    logger.info(f"GCS_PATH {gcs_path}")
    logger.info(f"File type {file_type}")
    logger.info("File processed")

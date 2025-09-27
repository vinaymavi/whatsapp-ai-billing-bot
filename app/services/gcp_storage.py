import logging

from google.cloud import storage

from app.config import get_settings
from app.utils.helpers import generate_temp_file_path

settings = get_settings()
logger = logging.getLogger(__name__)


class GCPStorage:
    bucket_name = settings.gcp_storage_bucket

    def __init__(self):
        try:
            self.client = storage.Client.from_service_account_json(
                settings.gcp_credentials_path
            )
            self.bucket = self.client.bucket(self.bucket_name)
        except Exception as e:
            logger.error(f"GCP storage initialization fails error: {e}")

    def upload_file(self, file_path: str, destination_blob_name: str) -> str:
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)

            logger.info(f"File uploaded to {destination_blob_name}")
            return destination_blob_name
        except Exception as e:
            logger.error(f"Error when uploading file to GCS error: {e}")

    def read_file(self, blob_name: str) -> bytes:
        try:
            blob = self.bucket.blob(blob_name)
            file_extension = blob_name.split(".")[-1]
            temp_file_path = generate_temp_file_path(file_extension)
            # Create a writable file object
            with open(temp_file_path, "wb") as f:
                blob.download_to_file(f)
            logger.info(f"File downloaded from {blob_name} to {temp_file_path}")
            return temp_file_path
        except Exception as e:
            logger.error(f"Error when reading file from GCS error: {e}")


gcp_storage = GCPStorage()

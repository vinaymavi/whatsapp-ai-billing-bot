import logging
from typing import Tuple
from uuid import uuid4

from fastapi import UploadFile
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

    def generate_unique_file_path(self, prefix: str, file_type: str) -> str:
        """
        Generate a unique file path with given prefix and file type.

        Accepts both traditional file extensions and content types.
        - File extensions: 'pdf', 'jpg', 'txt', 'html', etc.
        - Content types: 'application/pdf', 'image/jpeg', 'text/html', 'text/plain', etc.

        Args:
            prefix: Prefix for the file path (e.g., 'documents', 'images/user123')
            file_type: File extension or content type (e.g., 'pdf', 'application/pdf', 'jpg', 'image/jpeg')

        Returns:
            Unique file path string (e.g., 'documents/550e8400-e29b-41d4-a716-446655440000.pdf')
        """
        # Mapping of content types to file extensions
        content_type_to_extension = {
            "text/plain": "txt",
            "text/html": "html",
            "text/css": "css",
            "text/javascript": "js",
            "text/csv": "csv",
            "text/xml": "xml",
            "application/json": "json",
            "application/pdf": "pdf",
            "application/zip": "zip",
            "application/x-rar-compressed": "rar",
            "application/x-7z-compressed": "7z",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.ms-excel": "xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "application/vnd.ms-powerpoint": "ppt",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "image/webp": "webp",
            "image/svg+xml": "svg",
            "image/tiff": "tiff",
            "image/bmp": "bmp",
            "image/x-icon": "ico",
            "audio/mpeg": "mp3",
            "audio/wav": "wav",
            "audio/ogg": "ogg",
            "audio/flac": "flac",
            "audio/aac": "aac",
            "video/mp4": "mp4",
            "video/mpeg": "mpeg",
            "video/quicktime": "mov",
            "video/x-msvideo": "avi",
            "video/x-matroska": "mkv",
            "video/webm": "webm",
        }

        # Convert content type to extension if needed
        extension = content_type_to_extension.get(file_type.lower(), file_type.lower())

        # Remove leading dot if present
        if extension.startswith("."):
            extension = extension[1:]

        unique_id = uuid4()
        return f"{prefix}/{unique_id}.{extension}"

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

    async def upload_stream(
        self,
        file: UploadFile,
        destination_blob_name: str,
        chunk_size: int = 5 * 1024 * 1024,
    ) -> Tuple[str, str]:
        """
        Upload a file stream to GCS in chunks and return the GCS path and file type.

        Args:
            file: FastAPI UploadFile object
            destination_blob_name: Destination path in GCS
            chunk_size: Size of chunks to read at a time (default: 5MB)

        Returns:
            Tuple of (gcs_file_path, file_type)
        """
        try:
            blob = self.bucket.blob(destination_blob_name)

            # Upload file in chunks to handle large files efficiently
            with blob.open("wb", content_type=file.content_type) as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)

            logger.info(
                f"File streamed to GCS at {destination_blob_name} "
                f"with type {file.content_type}"
            )
            return destination_blob_name, file.content_type
        except Exception as e:
            logger.error(f"Error when uploading stream to GCS error: {e}")
            raise

    def read_stream(
        self,
        blob_name: str,
        chunk_size: int = 5 * 1024 * 1024,
    ) -> str:
        """
        Read a file stream from GCS bucket and save it to a temporary path.

        Args:
            blob_name: Path to the file in GCS bucket (e.g., 'batch-files/550e8400-e29b-41d4-a716-446655440000.pdf')
            chunk_size: Size of chunks to read at a time (default: 5MB)

        Returns:
            str: Complete temporary file path where the file was saved

        Raises:
            Exception: If error occurs during download or file operations
        """
        try:
            # Extract file extension from blob name
            file_extension = blob_name.split(".")[-1]
            temp_file_path = generate_temp_file_path(file_extension)

            blob = self.bucket.blob(blob_name)

            # Download file in chunks to handle large files efficiently
            with open(temp_file_path, "wb") as f:
                with blob.open("rb") as source_file:
                    while True:
                        chunk = source_file.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)

            logger.info(f"File streamed from GCS {blob_name} to {temp_file_path}")
            return temp_file_path
        except Exception as e:
            logger.error(f"Error when reading stream from GCS error: {e}")
            raise

    def move_blob(self, source_blob_name: str, destination_blob_name: str) -> str:
        """
        Move an existing blob to a new location and delete the original.

        Args:
            source_blob_name: Current path/name of the blob in GCS
            destination_blob_name: New path/name for the blob in GCS

        Returns:
            str: The new blob location (destination_blob_name)

        Raises:
            Exception: If error occurs during move operation
        """
        try:
            # Get reference to source blob
            source_blob = self.bucket.blob(source_blob_name)

            # Check if source blob exists
            if not source_blob.exists():
                raise FileNotFoundError(
                    f"Source blob {source_blob_name} does not exist"
                )

            # Copy the blob to the new location
            self.bucket.copy_blob(source_blob, self.bucket, destination_blob_name)

            # Delete the original blob
            source_blob.delete()

            logger.info(
                f"Blob moved from {source_blob_name} to {destination_blob_name}"
            )
            return destination_blob_name
        except Exception as e:
            logger.error(
                f"Error when moving blob from {source_blob_name} to {destination_blob_name}: {e}"
            )
            raise

    def move_to_documents_folder(self, source_blob_name: str) -> str:
        """
        Move an existing blob to the documents folder with a unique filename.

        Args:
            source_blob_name: Current path/name of the blob in GCS

        Returns:
            str: The new blob location in documents folder

        Raises:
            Exception: If error occurs during move operation
        """
        try:
            # Extract file extension from source blob name
            file_parts = source_blob_name.split(".")
            if len(file_parts) > 1:
                file_extension = file_parts[-1]
            else:
                # If no extension, use empty string
                file_extension = ""

            # Generate unique path in documents folder
            destination_blob_name = self.generate_unique_file_path(
                "documents", file_extension
            )

            # Use existing move_blob method to perform the move
            return self.move_blob(source_blob_name, destination_blob_name)

        except Exception as e:
            logger.error(
                f"Error when moving blob {source_blob_name} to documents folder: {e}"
            )
            raise


gcp_storage = GCPStorage()

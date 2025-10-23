from datetime import UTC, datetime
from enum import Enum
from typing import Dict
from uuid import uuid4

from pydantic import BaseModel

from app.services.db_service import db_service
from app.services.gcp_storage import gcp_storage
from app.services.vectordb_document_creator import DocumentCreator
from app.utils.global_logging import get_logger
from app.utils.helpers import remove_file_if_exists
from app.utils.whatsapp import download_whatsapp_media, send_whatsapp_message


class JobStatus(Enum):
    IN_PROGRESS = "in-progress"
    DONE = "done"
    FAILED = "failed"


class Job(BaseModel):
    sender_id: str
    type: str
    whatsapp_id: str


class DocumentJob(Job):
    doc_caption: str
    doc_filename: str
    doc_mime: str
    doc_id: str
    doc_hash: str


class WebDocumentJob(BaseModel):
    user_id: str
    doc_filename: str
    doc_mime: str
    gcs_path: str


DB_COLLECTION = "background_jobs"

logger = get_logger(__name__)


class BackgroundJob:
    def __init__(self):
        self.job_id = str(uuid4())
        self.data = {}

    def add_job_to_db(self, data: Dict):
        data.update({"job_id": self.job_id})
        data.update({"started_at": datetime.now(UTC)})
        db_service.write(DB_COLLECTION, self.job_id, data)
        self.data = self.data | data

    def update_job_status(self, status: JobStatus):
        if status == JobStatus.DONE or status == JobStatus.FAILED:
            self.data.update({"completed_at": datetime.now(UTC)})
        self.data.update({"status": str(status)})
        self.add_job_to_db(self.data)

    def update_job_progress(self, progress: Dict):
        if progress is not None and isinstance(progress, dict):
            progress.update({"at": datetime.now(UTC)})
        if "logs" in self.data and isinstance(self.data["logs"], list):
            self.data["logs"].append(progress)
        else:
            self.data.update({"logs": [progress]})
        self.add_job_to_db(self.data)


def process_document(document: DocumentJob):
    try:
        logger.info(f"Processing document job: {document.doc_id}")
        job = BackgroundJob()
        job.add_job_to_db(
            document.model_dump() | {"status": str(JobStatus.IN_PROGRESS)}
        )
        logger.info(f"Started processing document job: {job.job_id}")
        # Download the document from WhatsApp
        job.update_job_progress({"message": "Downloading document from WhatsApp..."})

        file_path = download_whatsapp_media(
            document.doc_id, "document", document.sender_id
        )

        job.update_job_progress({"message": "Downloaded document."})
        if file_path:
            # Process based on document type
            if document.doc_mime == "application/pdf":
                # Upload file to GCP Storage
                job.update_job_progress(
                    {"message": "Uploading document to GCP Storage..."}
                )
                gcp_blob_path = f"documents/{document.doc_filename}"
                job.update_job_progress({"message": f"Uploading to {gcp_blob_path}..."})
                gcp_storage.upload_file(file_path, gcp_blob_path)
                job.update_job_progress(
                    {"message": "Uploaded document to GCP Storage."}
                )
                # Process PDF document (e.g., extract bill information)
                # Index document in Vector DB
                job.update_job_progress(
                    {"message": "Indexing the document in pinecone..."}
                )
                bill_data = DocumentCreator.create_document_from_pdf(
                    file_path, gcp_blob_path
                )
                job.update_job_progress(
                    {"message": "Indexed the document in pinecone."}
                )

                # Send a response back to the user
                if bill_data.get("processed", False):
                    summary = bill_data.get("page_content", "")
                    job.update_job_status(JobStatus.DONE)
                    job.update_job_progress({"message": "Sending response to user..."})
                    response_msg = f"I've received your PDF document and processed it.\n*Summary:* {summary}"
                    # You could add more details from the processed data here
                else:
                    job.update_job_status(JobStatus.FAILED)
                    job.update_job_progress(
                        {"message": "Failed to process the document."}
                    )
                    response_msg = (
                        "I received your document but had trouble processing it."
                    )

                job.update_job_progress({"message": "Sending response to user..."})
                send_whatsapp_message(document.sender_id, response_msg)
                # Remove temporary files
                job.update_job_progress({"message": "Cleaning up temporary files..."})
                remove_file_if_exists(file_path)
            else:
                # Handle other document types
                logger.info(f"Unsupported document type: {document.doc_mime}")
                job.update_job_status(JobStatus.FAILED)
                job.update_job_progress({"message": "Unsupported document type."})
                send_whatsapp_message(
                    document.sender_id,
                    f"I received your document ({document.doc_filename}) but I don't know how to process this type of file yet.",
                )
        else:
            logger.error(f"Failed to download document: {document.doc_id}")
            job.update_job_status(JobStatus.FAILED)
            job.update_job_progress({"message": "Failed to download the document."})
            send_whatsapp_message(
                document.sender_id,
                "I had trouble downloading your document. Please try sending it again.",
            )
    except Exception as e:
        logger.error(f"Error processing document job {document.doc_id}: {e}")
        job.update_job_status(JobStatus.FAILED)
        job.update_job_progress(
            {"message": "An error occurred while processing the document."}
        )
        send_whatsapp_message(
            document.sender_id,
            "An error occurred while processing your document. Please try again later.",
        )


def process_web_document(
    web_document: WebDocumentJob, gcs_file_path: str, temp_file_path: str
):
    """
    Process a document uploaded from the web application.

    Args:
        web_document: WebDocumentJob containing document metadata
        gcs_file_path: Path to the file in GCS
        temp_file_path: Temporary local file path
    """
    try:
        logger.info(f"Processing web document job: {web_document.gcs_path}")
        job = BackgroundJob()
        job.add_job_to_db(
            web_document.model_dump() | {"status": str(JobStatus.IN_PROGRESS)}
        )
        logger.info(f"Started processing web document job: {job.job_id}")

        job.update_job_progress({"message": "Validating document..."})

        # Process based on document type
        if web_document.doc_mime == "application/pdf":
            # Index document in Vector DB
            job.update_job_progress({"message": "Indexing the document in pinecone..."})
            bill_data = DocumentCreator.create_document_from_pdf(
                temp_file_path, gcs_file_path
            )
            job.update_job_progress({"message": "Indexed the document in pinecone."})

            # Update job status based on processing result
            if bill_data.get("processed", False):
                job.update_job_status(JobStatus.DONE)
                job.update_job_progress({"message": "Document processing completed."})
                logger.info(
                    f"Successfully processed web document: {web_document.doc_filename}"
                )
            else:
                job.update_job_status(JobStatus.FAILED)
                job.update_job_progress({"message": "Failed to process the document."})
                logger.error(
                    f"Failed to process web document: {web_document.doc_filename}"
                )
        else:
            # Handle unsupported document types
            logger.info(
                f"Unsupported document type for web upload: {web_document.doc_mime}"
            )
            job.update_job_status(JobStatus.FAILED)
            job.update_job_progress({"message": "Unsupported document type."})

    except Exception as e:
        logger.error(f"Error processing web document job {web_document.gcs_path}: {e}")
        job.update_job_status(JobStatus.FAILED)
        job.update_job_progress(
            {"message": "An error occurred while processing the document."}
        )
    finally:
        # Clean up temporary file
        job.update_job_progress({"message": "Cleaning up temporary files..."})
        remove_file_if_exists(temp_file_path)

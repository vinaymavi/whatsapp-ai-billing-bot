import logging
from typing import Any, Dict

from langchain_core.documents import Document

from app.services.vector_db import vdb
from app.utils.document_processor import process_pdf_document

logger = logging.getLogger(__name__)
class DocumentCreator:
    vdb = vdb
    def __init__(self):
        pass

    @classmethod
    def create_document_from_pdf(cls, pdf_path: str) -> Dict[str, Any]:
        pdf_info = process_pdf_document(pdf_path)

        if not pdf_info.get("processed"):
            return pdf_info

        # Create a Document object from the extracted text
        document = Document(
            page_content=pdf_info.get("text", ""),
            metadata={"source": pdf_path}
        )

        cls.vdb.add_documents([document])
        
        return pdf_info
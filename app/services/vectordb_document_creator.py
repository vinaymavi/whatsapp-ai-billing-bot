import logging
from typing import Any, Dict

from langchain_core.documents import Document

from app.services.llm_service import llm_service
from app.services.vector_db import vdb
from app.utils.document_processor import process_pdf_document
from app.utils.types import VectorDBInvoiceData

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
        llm_resp:VectorDBInvoiceData = llm_service.query_with_structured_output(pdf_info.get("text",""),VectorDBInvoiceData)        
        # Create a Document object from the extracted text
        page_content = f"Provider: {llm_resp.provider}, Invoice Date: {llm_resp.invoice_date}, Invoice Items: {llm_resp.invoice_items}, Invoice Category: {llm_resp.invoice_category}"
        pdf_info['page_content'] = page_content
        document = Document(
            page_content=page_content,
            metadata= {
                "source": pdf_path,                
                "invoice_id": llm_resp.invoice_id,
                "invoice_date": llm_resp.invoice_date,
                "invoice_category": llm_resp.invoice_category,
                "invoice_items": llm_resp.invoice_items,
                "invoice_currency": llm_resp.invoice_currency,
                "customer_name": llm_resp.customer_name,
                "customer_id": llm_resp.customer_id,
                "customer_address": llm_resp.customer_address,
                "amount": llm_resp.amount,
                "status": llm_resp.status,
                "provider": llm_resp.provider,
                "summary": llm_resp.summary
            }
        )

        cls.vdb.add_documents([document])
        
        return pdf_info
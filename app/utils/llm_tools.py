import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.tools import tool

from app.services.db_service import db_service
from app.services.gcp_storage import gcp_storage
from app.services.vector_db import vdb
from app.utils.helpers import remove_file_if_exists
from app.utils.whatsapp import send_whatsapp_media

logger = logging.getLogger(__name__)
DB_COLLECTION_NAME = 'chat_history'

@tool
def delete_context(user_id: str) -> str:
    """
    Delete user context from database when user end the conversation. 
    Use can use normal communication terms to end the conversaion like by, thank you.
    """
    
    logger.info("Deleting user context")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Clearing chat history for user {user_id}")
    db_service.delete(DB_COLLECTION_NAME, user_id)
    logger.info(f"Chat history cleared for user {user_id}")
    # Code to delete user context from database goes here

    return "Current discussion context has been deleted from DB. We can send leaving greeting to the user."

@tool
def query_for_invoices(query: str) -> List[Document]:
    """
    User will be able to search/find/query the invoices by

    - Invoice provider
    - Invoice Items
    - Invoice by month and year
    - Invoice Category
    
    Vector DB is storing information in following format. 

    "Provider: Acme Inc. Date: 2024-06-15(YYYY-MM-DD) Item: Laptop Model XYZ Category: Electronics"
    
    Every invoice have some meta information stored with it. 
    
    meta key 'gcp_blob_path' is Google cloud storage file path. 
    this GCP path is to get the document from cloud storage.
    """
    logger.info(f"Searching vector DB for query: {query}")
    results = vdb.search(query)
   
    logger.info(f"Found {len(results)} documents")
   
    return f"Found {len(results)} documents matching your query. here is the results: ```{results}```"

@tool
def download_invoice(gcp_blob_path: str) -> str:
    """
    Download invoice document from Google Cloud Storage.

    Args:
        gcp_blob_path (str): The GCP blob path of the invoice document.

    Returns:
        str: Confirmation message.
    """
    logger.info(f"Downloading invoice from GCP: {gcp_blob_path}")
    temp_file_path  = gcp_storage.read_file(gcp_blob_path)
    # Code to download the invoice from GCP goes here
    return f"Invoice downloaded from GCP to this local file {temp_file_path}"

@tool
def send_downloaded_invoice_user(user_id: str, invoice_path: str, whats_app_file_caption: str, whats_app_file_name: str) -> str:
    """
    Send the downloaded invoice document to the user as WhatsApp message.

    Args:
        user_id (str): The ID of the user to send the invoice to.
        invoice_path (str): The local path to the downloaded invoice document.
        whats_app_file_caption (str): The caption for the WhatsApp file message. 
        whats_app_file_name (str): The filename for the WhatsApp file message.

    Returns:
        str: Confirmation message.
    """
    logger.info(f"Sending downloaded invoice to user {user_id}: {invoice_path}")
    success, message = send_whatsapp_media(user_id, invoice_path, whats_app_file_caption, whats_app_file_name)
    if not success:
        logger.error(f"Failed to send invoice to user {user_id}: {message}")
        return f"Failed to send invoice to user {user_id}: {message}"
    # Remove temporary files
    remove_file_if_exists(invoice_path) 
    return f"Invoice sent to user {user_id}: {invoice_path}"

functions = {
    "delete_context": delete_context,
    "query_for_invoices": query_for_invoices,
    "download_invoice": download_invoice,
    "send_downloaded_invoice_user": send_downloaded_invoice_user
}

llm_tools:List[Any] = [delete_context, query_for_invoices, download_invoice, send_downloaded_invoice_user]


def run_llm_tools(tools:List[Dict[str, Any]], history:Any, user_id: str) -> Any:
    for tool in tools:
        tool_name = tool.get("name")
        tool_args = tool.get("args", {})
        tool_call_id = tool.get("id", "")
        tool_func = functions.get(tool_name, None)


        if callable(tool_func):
            try:
                logger.info(f"Invoking tool: {tool_name} with args: {tool_args}")
                resp = tool_func.invoke(tool_args | {"user_id": user_id})
            except Exception as e:
                logger.error(f"Error invoking tool {tool_name}: {str(e)}")
                resp = str(e)
            history.add_tool_message(resp, tool_call_id=tool_call_id)
    return history


import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.tools import tool

from app.services.db_service import db_service
from app.services.vector_db import vdb

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
    User will be able to search/find/query the invoides by 
    
    - Invoice provider 
    - Invoice Items
    - Invoice by month and year
    - Invoice Category
    
    Vector DB is storing information in following format. 

    "Provider: Acme Inc. Date: 2024-06-15(YYYY-MM-DD) Item: Laptop Model XYZ Category: Electronics"
    """
    logger.info(f"Searching vector DB for query: {query}")
    results = vdb.search(query)
    logger.info(f"Found {len(results)} documents")
    return f"Found {len(results)} documents matching your query. here is the results: ```{results}```"

functions = {
    "delete_context": delete_context,
    "query_for_invoices": query_for_invoices
}

llm_tools:List[Any] = [delete_context, query_for_invoices]


def run_llm_tools(tools:List[Dict[str, Any]], history:Any, user_id: str) -> Any:
    for tool in tools:
        tool_name = tool.get("name")
        tool_args = tool.get("args", {})
        tool_call_id = tool.get("id", "")
        tool_func = functions.get(tool_name, None)

        if callable(tool_func):
            resp = tool_func.invoke(tool_args | {"user_id": user_id})
            history.add_tool_message(resp, tool_call_id=tool_call_id)
    return history


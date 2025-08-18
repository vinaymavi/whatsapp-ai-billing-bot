import datetime
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage, ToolMessage)

logger = logging.getLogger(__name__)

def langchain_msg_to_dict(msgs: List[BaseMessage]) -> List[Dict]:
    result = []
    for msg in msgs:
        msg_dict = {
            'type': type(msg).__name__.replace('Message', '').lower(),
            'text': msg.content            
        }
        
        if hasattr(msg, 'tool_call_id') and msg.tool_call_id is not None:
            msg_dict['tool_call_id'] = msg.tool_call_id


        if hasattr(msg, 'tool_calls') and msg.tool_calls is not None:
            msg_dict['tool_calls'] = msg.tool_calls

        result.append(msg_dict)
    return result
    
def list_to_langchain_msg(_list:List[Dict])->List[BaseMessage] :
    lang_chain_msgs:List[BaseMessage] = []
    
    for msg in _list:
        if msg['type'] == 'human': 
            lang_chain_msgs.append(HumanMessage(msg['text']))
        if msg['type'] == 'ai':
            lang_chain_msgs.append(AIMessage(msg['text'], tool_calls=msg.get('tool_calls', [])))
        if msg['type'] == 'system': 
            lang_chain_msgs.append(SystemMessage(msg['text']))
        if msg['type'] == 'tool': 
            lang_chain_msgs.append(ToolMessage(msg['text'], tool_call_id=msg.get('tool_call_id', '')))

    return lang_chain_msgs


def get_ttl_key(ttl_seconds: Optional[int] = 300) -> Dict:
    """
    Returns a dictionary with a TTL key for Firebase database.
    The key is 'expires_at' and the value is a Unix timestamp in seconds.
    """
    return {"expires_at": datetime.now(UTC) + timedelta(seconds=ttl_seconds)}


def generate_temp_file_path(extension: str) -> str:
    """
    Generates a temporary file path for storing downloaded files.

    Returns:
        str: The temporary file path.
    """
    return f"/tmp/{uuid.uuid4()}.{extension}"

    
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)

logger = logging.getLogger(__name__)

def langchain_msg_to_dict(msgs: List[BaseMessage]) -> List[Dict]:
    return [
        {
            'type': type(msg).__name__.replace('Message', '').lower(),
            'text': msg.content
        }
        for msg in msgs
    ]
    
def list_to_langchain_msg(_list:List[Dict])->List[BaseMessage] :
    lang_chain_msgs:List[BaseMessage] = []
    
    for msg in _list:
        if msg['type'] == 'human': 
            lang_chain_msgs.append(HumanMessage(msg['text']))
        if msg['type'] == 'ai':
            lang_chain_msgs.append(AIMessage(msg['text']))
        if msg['type'] == 'system': 
            lang_chain_msgs.append(SystemMessage(msg['text']))
    
    return lang_chain_msgs


def get_ttl_key(ttl_seconds: Optional[int] = 300) -> Dict:
    """
    Returns a dictionary with a TTL key for Firebase database.
    The key is 'expires_at' and the value is a Unix timestamp in seconds.
    """
    return {"expires_at": datetime.now() + timedelta(seconds=ttl_seconds)}

    
    
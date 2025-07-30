from typing import Dict, List

from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)


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
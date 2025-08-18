import logging
from typing import Dict, List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage, ToolCall, ToolMessage,
                                     trim_messages)
from langchain_core.messages.utils import count_tokens_approximately

from app.services.db_service import FirestoreService, db_service
from app.utils.helpers import langchain_msg_to_dict, list_to_langchain_msg
from app.utils.prompt import system_prompt

DB_COLLECTION_NAME = 'chat_history'
class FirebaseChatHistory(BaseChatMessageHistory):
    db:FirestoreService = db_service

    def __init__(self, use_id:str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Chat history created for user {use_id}")
        self.user_id:str = use_id;
        self.messages:List[BaseMessage] = []
        self._get_messages()
        

    def add_message(self, message:BaseMessage):
        try:
            self.messages.append(message)
        except Exception as e: 
            self.logger.error(e)    

    def add_messages(self, messages:List[BaseMessage]):
        try:
            self.messages.extend(messages)
        except Exception as e:
            self.logger.error(e)
        
    def commit(self):
        self._write()
        
    def _get_messages(self):
        doc_dict = self.db.read(DB_COLLECTION_NAME, self.user_id)
        messages = doc_dict.get('messages', []) if doc_dict else []
        langchain_msgs = list_to_langchain_msg(messages)

        if len(langchain_msgs) == 0:
                langchain_msgs.append(system_prompt)
        
        self.messages = langchain_msgs
        # If doc_dict is empty create an empty document in DB
        if not doc_dict:
            self._create_empty_message_list()

    def add_human_message(self, msg:str, whatsapp_msg_id:str = None):
        human_msg = HumanMessage(f'{msg}  |  latest_whatsapp_msg_id={whatsapp_msg_id}')
        self.add_message(human_msg)
    
    def add_ai_message(self, msg:str, tool_calls:list[ToolCall]=[]):
        self.add_message(AIMessage(msg, tool_calls=tool_calls))
        
    def add_tool_message(self,msg:str, tool_call_id:str):
        self.add_message(ToolMessage(content=msg, tool_call_id=tool_call_id))

    def clear(self):
        self.db.delete(DB_COLLECTION_NAME, self.user_id)

    def _create_empty_message_list(self):
        FirebaseChatHistory.db.write_with_ttl(DB_COLLECTION_NAME, self.user_id, {"messages": []})
    
    def _trim_messages(self):
        self.messages = trim_messages(
            self.messages, 
            strategy="last",
            include_system=True,
            start_on="human",
            max_tokens=18000,
            token_counter=count_tokens_approximately
            )
        
    def _write(self):
        # Write messages to the database when document exists
        doc_dict = self.db.read(DB_COLLECTION_NAME, self.user_id)
        if not doc_dict:
            self.logger.warning(f"No document found for user {self.user_id}. Not able to commit")
            return
        self._trim_messages()
        _list = langchain_msg_to_dict(self.messages)
        self.db.write_with_ttl(DB_COLLECTION_NAME,self.user_id, {"messages": _list})
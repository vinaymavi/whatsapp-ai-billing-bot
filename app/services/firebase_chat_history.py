import logging
from typing import Dict, List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)

from app.services.db_service import FirestoreService, db_service
from app.utils.helpers import langchain_msg_to_dict, list_to_langchain_msg


class FirebaseChatHistory(BaseChatMessageHistory):
    db:FirestoreService = db_service    
    DB_COLLECTOIN_NAME = 'chat_history'    
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
        doc_dict = self.db.read(self.DB_COLLECTOIN_NAME, self.user_id)
        messges = doc_dict.get('messages', [])
        langchain_msgs =  list_to_langchain_msg(messges)
        self.messages = langchain_msgs
        
    def add_human_message(self, msg:str):
        human_msg = HumanMessage(msg)
        self.add_message(human_msg)
    
    def add_ai_message(self, msg:str):
        self.add_message(AIMessage(msg))
        
    def clear(self):
        self.logger.info('Clear history')
        
    def _write(self):
        _list = langchain_msg_to_dict(self.messages)
        self.db.write(self.DB_COLLECTOIN_NAME,self.user_id, {"messages": _list})
    
"""
LLM Service - Model-Agnostic LLM Provider

This service provides a unified interface to interact with different LLM providers
using the LangChain framework. The provider is selected based on the LLM_PROVIDER
environment variable. Supported providers can be extended easily.
"""

# Add more imports as needed for other providers
import logging
import os
from typing import Any, Dict, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
# Import supported LangChain LLMs here
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.utils.llm_tools import delete_context  # Import the tool
from app.utils.prompt import prompt_v1  # Import the prompt template
from app.utils.types import LLMResponse  # Import the LLMResponse type

logger = logging.getLogger(__name__)


class LLMService:
    tools = [delete_context]

    """
    LLMService dynamically selects and initializes an LLM instance
    based on the LLM_PROVIDER environment variable.
    """
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
        self.llm_with_tools = self._get_llm_instance_with_tools()
        self.llm = self._get_llm_instance()

    def _get_llm_instance(self) -> BaseChatModel:
            """
            Returns an LLM instance based on the provider.
            Extend this method to support more providers.
            """
            if self.provider == "openai":
                # Reads OpenAI API key from env var OPENAI_API_KEY
                return ChatOpenAI(model=self.model_name, temperature=0.7, max_completion_tokens=500)
            # Add more providers here as needed
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
    def _get_llm_instance_with_tools(self) -> BaseChatModel:
        """
        Returns an LLM instance based on the provider.
        Extend this method to support more providers.
        """
        if self.provider == "openai":
            # Reads OpenAI API key from env var OPENAI_API_KEY
            return ChatOpenAI(model=self.model_name, temperature=0.7, max_completion_tokens=500).bind_tools(self.tools)
        # Add more providers here as needed
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate a response from the LLM for the given prompt.
        """
        logger.info(f"Generating response using {self.provider} provider with model {self.model_name}")
        logger.info(f"Prompt: {prompt}")
        resp =  self.llm_with_tools.invoke(prompt, **kwargs)
        logger.info(f"{resp}")
        return self._send_resp(resp)
    
    def _send_resp(self, resp:Any) -> LLMResponse:
        """
        Send the response back to the user.        
        """
        
        if hasattr(resp, 'tool_calls') and isinstance(resp.tool_calls, list) and len(resp.tool_calls) > 0:
            return LLMResponse(
                type="tool_calls",
                tool_calls=resp.tool_calls
            )
        elif hasattr(resp, 'content') and len(resp.content) > 0:
            content_length = len(resp.content) if isinstance(resp.content, str) else 0
            logger.info(f"Response content length: {content_length}")
            return LLMResponse(
                type="message",
                text=resp.content
            )
            
        return LLMResponse(
            type="message",
            text=str(resp)
        )

    def query(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Query the LLM with a specific prompt.
        """       
        logger.info(f" Prompt : {prompt}")
        return self._generate(prompt, **kwargs)
    
    def format_and_query(self, messages:List[BaseMessage]) -> LLMResponse:
        template = ChatPromptTemplate(messages=messages)
        return self.query(template.format())

    def query_with_structured_output(self, messages: str, structure: BaseModel):
        structured_llm = self.llm.with_structured_output(structure)

        resp = structured_llm.invoke(messages)
        logger.info(f"Structured response: {resp}")
        return resp

# Singleton instance for app-wide use
llm_service = LLMService()

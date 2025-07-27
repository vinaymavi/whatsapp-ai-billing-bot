"""
LLM Service - Model-Agnostic LLM Provider

This service provides a unified interface to interact with different LLM providers
using the LangChain framework. The provider is selected based on the LLM_PROVIDER
environment variable. Supported providers can be extended easily.
"""

# Add more imports as needed for other providers
import logging
import os
from typing import Any

from langchain_core.language_models import BaseChatModel
# Import supported LangChain LLMs here
from langchain_openai import ChatOpenAI

from app.utils.prompt import prompt_v1  # Import the prompt template

logger = logging.getLogger(__name__)
class LLMService:
    """
    LLMService dynamically selects and initializes an LLM instance
    based on the LLM_PROVIDER environment variable.
    """
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
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

    def _generate(self, prompt: str, **kwargs) -> Any:
        """
        Generate a response from the LLM for the given prompt.
        """
        logger.info(f"Generating response using {self.provider} provider with model {self.model_name}")
        logger.info(f"Prompt: {prompt}")
        resp =  self.llm.invoke(prompt, **kwargs)
        return resp.content if hasattr(resp, 'content') else str(resp)
    
    def query(self, query: str, **kwargs) -> Any:
        """
        Query the LLM with a specific query.
        """
        prompt = prompt_v1.format(query=query)        
        return self._generate(prompt, **kwargs)

# Singleton instance for app-wide use
llm_service = LLMService()

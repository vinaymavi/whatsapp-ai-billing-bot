"""
LLM Service - Model-Agnostic LLM Provider

This service provides a unified interface to interact with different LLM providers
using the LangChain framework. The provider is selected based on the LLM_PROVIDER
environment variable. Supported providers can be extended easily.
"""

import os
from typing import Any

from langchain_core.language_models import BaseChatModel
# Import supported LangChain LLMs here
from langchain_openai import ChatOpenAI

# Add more imports as needed for other providers

class LLMService:
    """
    LLMService dynamically selects and initializes an LLM instance
    based on the LLM_PROVIDER environment variable.
    """
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.llm = self._get_llm_instance()

    def _get_llm_instance(self) -> BaseChatModel:
        """
        Returns an LLM instance based on the provider.
        Extend this method to support more providers.
        """
        if self.provider == "openai":
            # Reads OpenAI API key from env var OPENAI_API_KEY
            return ChatOpenAI()
        # Add more providers here as needed
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str, **kwargs) -> Any:
        """
        Generate a response from the LLM for the given prompt.
        """
        resp =  self.llm.invoke(prompt, **kwargs)
        return resp.content if hasattr(resp, 'content') else str(resp)

# Singleton instance for app-wide use
llm_service = LLMService()

"""
Configuration settings for the WhatsApp Billing Bot application.

This module loads environment variables and provides configuration
settings for the application through the Settings class.
"""

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    
    webhook_token: str = Field(alias="WEBHOOK_TOKEN")

    # WhatsApp API Settings
    whatsapp_api_token: str = Field(alias="WHATSAPP_API_TOKEN")
    whatsapp_phone_number_id: str = Field(alias="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_business_account_id: str = Field(alias="WHATSAPP_BUSINESS_ACCOUNT_ID")
    
    # OpenAI Settings
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    
    # Google Cloud Settings
    gcp_project_id: str = Field(alias="GCP_PROJECT_ID")
    gcp_location: str = Field(default="us-central1", alias="GCP_LOCATION")
    gcp_credentials_path: str = Field(alias="GCP_CREDENTIALS_PATH")
    gcp_storage_bucket: str = Field(default="chabot-files", alias="GCP_STORAGE_BUCKET")
    
    # Firestore Settings
    firestore_collection_chat_history: str = Field(default="chat_history", alias="FIRESTORE_COLLECTION_CHAT_HISTORY")
    firestore_collection_processed_messages: str = Field(default="processed_messages", alias="FIRESTORE_COLLECTION_PROCESSED_MESSAGES")

    # Pinecone Settings
    pinecone_api_key: str = Field(alias="PINECONE_API_KEY")
    pinecone_index_name: str = Field(alias="PINECONE_INDEX_NAME")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings as a singleton using lru_cache.
    
    Returns:
        Settings: Application settings singleton instance
    """
    return Settings()
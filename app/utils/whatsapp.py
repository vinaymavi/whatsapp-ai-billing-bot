"""
WhatsApp API Utilities

This module provides utility functions for interacting with the WhatsApp Cloud API,
including downloading media, sending messages, and processing webhook events.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import requests

logger = logging.getLogger(__name__)

def check_whatsapp_token(settings) -> bool:
    """
    Check if the WhatsApp API token is valid.
    
    Args:
        settings: Application settings with WhatsApp API credentials
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}"
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_api_token}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            logger.info("WhatsApp API token is valid")
            return True
        else:
            logger.error(f"WhatsApp API token validation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error checking WhatsApp API token: {str(e)}")
        return False

def download_whatsapp_media(
    media_id: str, 
    media_type: str, 
    sender_id: str, 
    settings
) -> Optional[str]:
    """
    Download media (image, document, audio) from WhatsApp Cloud API.
    
    Args:
        media_id (str): The WhatsApp media ID
        media_type (str): Type of media (image, document, audio)
        sender_id (str): The sender's WhatsApp ID
        settings: Application settings with WhatsApp API credentials
        
    Returns:
        Optional[str]: Path to the downloaded file or None if download failed
    """
    try:
        # Create the media directory if it doesn't exist
        media_dir = Path("media") / media_type
        os.makedirs(media_dir, exist_ok=True)
        
        # Generate a unique filename
        file_path = media_dir / f"{sender_id}_{media_id}.bin"
        
        # Step 1: Get the media URL
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_api_token}"
        }
        
        # Log details for debugging
        logger.info(f"Attempting to get media URL for {media_type} with ID: {media_id}")
        response = requests.get(url, headers=headers)
        
        # Log the response for debugging
        if response.status_code != 200:
            logger.error(f"Media URL fetch error: {response.status_code} - {response.text}")
            
        response.raise_for_status()
        
        media_data = response.json()
        media_url = media_data.get('url')
        
        if not media_url:
            logger.error(f"Failed to get URL for media ID: {media_id}")
            return None
        
        # Step 2: Download the media
        response = requests.get(
            media_url,
            headers=headers,
            stream=True
        )
        response.raise_for_status()
        
        # Save the media to a file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded {media_type} to {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error downloading {media_type}: {str(e)}")
        return None

def send_whatsapp_message(
    recipient_id: str, 
    message_text: str,
    settings
) -> Tuple[bool, str]:
    """
    Send a text message via WhatsApp Cloud API.
    
    Args:
        recipient_id (str): The recipient's WhatsApp ID
        message_text (str): The message to send
        settings: Application settings with WhatsApp API credentials
        
    Returns:
        Tuple[bool, str]: (Success status, Message or error)
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.whatsapp_api_token}"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        logger.info(f"Sending message to {recipient_id} via WhatsApp API")
        response = requests.post(url, headers=headers, json=data)
        
        # Log the response for debugging
        if response.status_code != 200:
            logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
            
        response.raise_for_status()
        
        result = response.json()
        message_id = result.get('messages', [{}])[0].get('id')
        
        logger.info(f"Message sent to {recipient_id}, ID: {message_id}")
        return True, message_id
        
    except Exception as e:
        error_msg = f"Error sending message: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

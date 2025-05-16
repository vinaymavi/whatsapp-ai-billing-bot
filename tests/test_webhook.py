"""
Tests for WhatsApp webhook endpoints
"""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_whatsapp_webhook_verification_success():
    """Test the WhatsApp webhook verification with valid parameters."""
    # Mock the settings to provide a known API token
    with patch("app.config.get_settings") as mock_get_settings:
        # Configure the mock settings
        mock_settings = mock_get_settings.return_value
        mock_settings.whatsapp_api_token = "test_verify_token"
        
        # Make the request with valid parameters
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_verify_token",
                "hub.challenge": "challenge_string"
            }
        )
        
        assert response.status_code == 200
        assert response.text == "challenge_string"

def test_whatsapp_webhook_verification_failure():
    """Test the WhatsApp webhook verification with invalid token."""
    # Mock the settings to provide a known API token
    with patch("app.config.get_settings") as mock_get_settings:
        # Configure the mock settings
        mock_settings = mock_get_settings.return_value
        mock_settings.whatsapp_api_token = "test_verify_token"
        
        # Make the request with invalid token
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "challenge_string"
            }
        )
        
        assert response.status_code == 403

def test_whatsapp_webhook_message_handling():
    """Test the WhatsApp webhook POST endpoint for message handling."""
    # Sample message payload based on WhatsApp Cloud API format
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "1234567890"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Test User"
                                    },
                                    "wa_id": "9876543210"
                                }
                            ],
                            "messages": [
                                {
                                    "id": "message_id_123",
                                    "from": "9876543210",
                                    "timestamp": "1632825646",
                                    "type": "text",
                                    "text": {
                                        "body": "Bill for $100 from Electricity Company"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    # Mock dependencies
    with patch("app.config.get_settings") as mock_get_settings, \
         patch("app.main.process_whatsapp_message") as mock_process:
        # Configure mock settings
        mock_settings = mock_get_settings.return_value
        mock_settings.whatsapp_business_account_id = "123456789"
        
        # Setup mock for process_whatsapp_message to return immediately
        mock_process.return_value = None
        
        # Make the request
        response = client.post(
            "/webhook/whatsapp",
            json=payload
        )
        
        # Verify the response
        assert response.status_code == 200
        assert response.json() == {"success": True}
        
        # Verify message was processed
        mock_process.assert_called_once()
        
        # Extract the first argument (message) passed to process_whatsapp_message
        message_arg = mock_process.call_args[0][0]
        assert message_arg["id"] == "message_id_123"
        assert message_arg["type"] == "text"
        assert message_arg["text"]["body"] == "Bill for $100 from Electricity Company"

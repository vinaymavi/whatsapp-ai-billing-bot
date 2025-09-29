"""
Tests for WhatsApp webhook endpoints
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(scope="function")
def mock_settings_class():
    from app.config import get_settings

    get_settings.cache_clear()  # Clear the cache to allow mocking
    with patch("app.config.Settings") as mock_settings_class:
        yield mock_settings_class.return_value

        get_settings.cache_clear()  # Clear the cache to allow mocking


@pytest.fixture
def mock_process_whatsapp_message():
    with patch("app.main.process_whatsapp_message") as mock_process_whatsapp_message:
        mock_process_whatsapp_message.return_value = None
        yield mock_process_whatsapp_message


def test_whatsapp_webhook_verification_success(mock_settings_class):
    """Test the WhatsApp webhook verification with valid parameters."""

    # Configure the mock settings
    mock_settings_class.webhook_token = "test_verify_token"

    # Make the request with valid parameters
    response = client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test_verify_token",
            "hub.challenge": "challenge_string",
        },
    )

    assert response.status_code == 200
    assert response.text == "challenge_string"


def test_whatsapp_webhook_verification_failure(mock_settings_class):
    """Test the WhatsApp webhook verification with invalid token."""

    # Configure the mock settings
    mock_settings = mock_settings_class.return_value
    mock_settings.webhook_token = "test_verify_token"

    # Make the request with invalid token
    response = client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "challenge_string",
        },
    )

    assert response.status_code == 403


def test_whatsapp_webhook_message_handling(
    mock_settings_class, mock_process_whatsapp_message
):
    """Test the WhatsApp webhook POST endpoint for message handling."""
    from app.config import get_settings

    get_settings.cache_clear()  # Clear the cache to allow mocking
    mock_settings_class.whatsapp_business_account_id = "123456789"
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
                                "phone_number_id": "1234567890",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": "9876543210",
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
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    # Make the request
    response = client.post("/webhook/whatsapp", json=payload)

    # Verify the response
    assert response.status_code == 200
    assert response.json() == {"success": True}

    # Verify message was processed
    mock_process_whatsapp_message.assert_called_once()

    # Extract the first argument (message) passed to process_whatsapp_message
    message_arg = mock_process_whatsapp_message.call_args[0][0]
    assert message_arg["id"] == "message_id_123"
    assert message_arg["type"] == "text"
    assert message_arg["text"]["body"] == "Bill for $100 from Electricity Company"

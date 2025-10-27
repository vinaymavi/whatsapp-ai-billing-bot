"""
@Deprecated No longer used
AI Service Module

This module contains utilities for using OpenAI's API to analyze and extract information
from text, including bill details, invoice information, and other financial data.
"""

import json
import logging
from typing import Any, Dict, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


def analyze_text_with_openai(
    text: str, prompt_type: str, settings
) -> Optional[Dict[str, Any]]:
    """
    Analyze text using OpenAI's API to extract structured information.

    Args:
        text (str): The text to analyze
        prompt_type (str): Type of analysis to perform (e.g., 'bill', 'invoice')
        settings: Application settings with OpenAI API credentials

    Returns:
        Optional[Dict[str, Any]]: Structured data extracted from the text
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.openai_api_key)

        # Define system prompts based on analysis type
        system_prompts = {
            "bill": (
                "You are an expert financial assistant that extracts structured billing information from text. "
                "Extract the following information (if available): "
                "1. Merchant/Company Name "
                "2. Date of Purchase/Service "
                "3. Total Amount "
                "4. Tax Amount "
                "5. Line Items (with prices) "
                "6. Payment Method "
                "7. Invoice/Receipt Number"
            ),
            "invoice": (
                "You are an expert financial assistant that extracts structured invoice information from text. "
                "Extract the following information (if available): "
                "1. Vendor Name "
                "2. Invoice Date "
                "3. Due Date "
                "4. Invoice Number "
                "5. Line Items (with prices) "
                "6. Subtotal "
                "7. Tax Amount "
                "8. Total Amount "
                "9. Payment Terms"
            ),
        }

        # Select appropriate system prompt
        system_prompt = system_prompts.get(prompt_type, system_prompts["bill"])

        # Create the message content
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Extract structured data from this text: \n\n{text}\n\n"
                    "Return the data as a JSON object with appropriate fields."
                ),
            },
        ]

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Use the most capable model available
            messages=messages,
            temperature=0,  # Lower temperature for more deterministic outputs
            response_format={"type": "json_object"},  # Request JSON output
        )

        # Extract and parse the response
        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        logger.info(f"Successfully analyzed text using OpenAI ({prompt_type})")
        return result

    except Exception as e:
        logger.error(f"Error analyzing text with OpenAI: {str(e)}")
        return None


def generate_bill_summary(bill_data: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of bill information.

    Args:
        bill_data (Dict[str, Any]): The structured bill data

    Returns:
        str: Human-readable summary
    """
    try:
        # Extract key information
        merchant = bill_data.get(
            "merchant_name", bill_data.get("vendor_name", "Unknown Merchant")
        )
        date = bill_data.get("date", bill_data.get("invoice_date", "Unknown Date"))
        total = bill_data.get("total_amount", bill_data.get("total", "Unknown Amount"))

        # Generate summary
        summary = f"📝 *Bill Summary*\n\n"
        summary += f"*Merchant:* {merchant}\n"
        summary += f"*Date:* {date}\n"
        summary += f"*Total:* {total}\n"

        # Add line items if available
        items = bill_data.get("line_items", bill_data.get("items", []))
        if items and isinstance(items, list) and len(items) > 0:
            summary += "\n*Items:*\n"
            for item in items[:5]:  # Limit to 5 items to avoid very long messages
                if isinstance(item, dict):
                    item_name = item.get("name", item.get("description", "Item"))
                    item_price = item.get("price", item.get("amount", "Unknown Price"))
                    summary += f"- {item_name}: {item_price}\n"
                elif isinstance(item, str):
                    summary += f"- {item}\n"

            if len(items) > 5:
                summary += f"- and {len(items) - 5} more items...\n"

        # Add payment information if available
        payment_method = bill_data.get("payment_method", bill_data.get("payment", ""))
        if payment_method:
            summary += f"\n*Payment Method:* {payment_method}"

        return summary

    except Exception as e:
        logger.error(f"Error generating bill summary: {str(e)}")
        return "I processed your bill but couldn't generate a summary. Please check the details."

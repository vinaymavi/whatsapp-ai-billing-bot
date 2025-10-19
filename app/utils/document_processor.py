"""
Document Processing Utilities

This module provides utilities for processing various document types,
including PDFs, Excel spreadsheets, and other file formats that may contain
billing information.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def process_pdf_document(file_path: str) -> Dict[str, Any]:
    """
    Process a PDF document to extract text information.

    Args:
        file_path (str): Path to the PDF file
    Returns:
        Dict[str, Any]: Extracted text information
    """
    try:
        pdf_reader = PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        logger.info(f"Extracted text from PDF:\n{text} \n **************************\n")

        return {"processed": True, "text": text}

    except Exception as e:
        logger.error(f"Error processing PDF document: {str(e)}")
        return {"processed": False, "error": str(e)}


def process_excel_document(file_path: str, sender_id: str, settings) -> Dict[str, Any]:
    """
    Process an Excel document to extract billing information.

    Args:
        file_path (str): Path to the Excel file
        sender_id (str): The sender's WhatsApp ID
        settings: Application settings

    Returns:
        Dict[str, Any]: Extracted billing information
    """
    try:
        # You would implement Excel processing here
        # This could involve:
        # 1. Using pandas, openpyxl, or a similar library to read the Excel file
        # 2. Analyzing the data to identify billing information
        # 3. Returning the structured billing data

        logger.info(f"Processing Excel document: {file_path}")

        # Example placeholder result
        result = {
            "processed": True,
            "file_path": file_path,
            "sender_id": sender_id,
            "extracted_data": {
                "detected_type": "bill_data",
                "sheets": [],
                "items": [],
                "total": 0.0,
            },
        }

        return result

    except Exception as e:
        logger.error(f"Error processing Excel document: {str(e)}")
        return {"processed": False, "error": str(e)}


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using OCR.

    Args:
        image_path (str): Path to the image file

    Returns:
        str: Extracted text
    """
    try:
        # Import the required libraries
        import cv2
        import numpy as np
        import pytesseract
        from PIL import Image

        logger.info(f"Extracting text from image: {image_path}")

        # Read the image
        img = cv2.imread(image_path)

        if img is None:
            logger.error(f"Failed to read image at {image_path}")
            return ""

        # Preprocess the image to improve OCR accuracy
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply threshold to get image with only black and white pixels
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Noise removal
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

        # Save the preprocessed image to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        cv2.imwrite(temp_file.name, denoised)

        # Perform OCR on the preprocessed image
        custom_config = r"--oem 3 --psm 6"  # OCR Engine mode and Page Segmentation mode
        text = pytesseract.image_to_string(
            Image.open(temp_file.name), config=custom_config
        )

        # Clean up the temporary file
        temp_file.close()
        os.unlink(temp_file.name)

        if not text.strip():
            logger.warning("No text detected in the image")
            return ""

        logger.info(f"Successfully extracted {len(text)} characters from image")
        return text

    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return ""

"""
WhatsApp Billing Bot - Main Application Entry Point

This module initializes the FastAPI application and includes all the routes
for the application. It serves as the entry point for the WhatsApp billing bot.
"""

import json
import logging
import os
from datetime import UTC, datetime

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.services.ai_service import (analyze_text_with_openai,
                                     generate_bill_summary)
from app.utils.document_processor import (extract_text_from_image,
                                          process_excel_document,
                                          process_pdf_document)
from app.utils.whatsapp import (check_whatsapp_token, download_whatsapp_media,
                                send_whatsapp_message)

# Configure logging based on settings
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.info(f"Starting application with log level: {settings.log_level}")

# Validate WhatsApp API token
token_valid = check_whatsapp_token(settings)
if not token_valid:
    logger.warning("WhatsApp API token validation failed. Some functionality may not work.")

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp Billing Bot API",
    description="API for WhatsApp billing automation with AI capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check endpoint
@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Status information including version and current time
    """
    return {
        "status": "healthy",
        "version": app.version,
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.environment
    }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that redirects to the documentation.
    
    Returns:
        dict: Welcome message and API information
    """
    return {
        "message": "Welcome to WhatsApp Billing Bot API",
        "documentation": "/docs",
        "health": "/health"
    }

# WhatsApp webhook verification endpoint
@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(request: Request, settings: Settings = Depends(get_settings)):
    """
    Verification endpoint for WhatsApp webhook setup.
    
    WhatsApp Cloud API sends a verification request with mode, challenge, and token.
    This endpoint must return the challenge to complete the verification process.
    
    Args:
        request: The verification request
        settings: Application settings
        
    Returns:
        The challenge string or an error response
    """
    # Get query parameters
    params = request.query_params
    
    # WhatsApp sends these verification parameters
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    # Define a verification token (should be set in environment variables)
    verify_token = settings.webhook_token
    
    # Verify the mode and token
    if mode == "subscribe" and token == verify_token:
        # Return the challenge to complete verification
        if challenge:
            return Response(content=challenge, media_type="text/plain")
        return Response(status_code=400, content="No challenge provided")
    
    # Return error if verification fails
    return Response(status_code=403, content="Verification failed")

# WhatsApp webhook endpoint for receiving messages
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, settings: Settings = Depends(get_settings)):
    """
    Webhook endpoint to receive messages from WhatsApp Cloud API.
    
    This endpoint:
    1. Verifies the WhatsApp message format
    2. Processes incoming messages
    3. Returns appropriate response to WhatsApp
    
    Args:
        request: The incoming HTTP request containing WhatsApp message data
        settings: Application settings
        
    Returns:
        dict: Confirmation of receipt or error message
    """
    try:
        # Parse the request body
        body = await request.json()
        logger.info(f"Received webhook: {json.dumps(body, indent=2)}")
        #print(f"Received webhook: {json.dumps(body, indent=2)}")
        # Log the incoming request for debugging
        
        # Check if this is a valid WhatsApp message
        if 'object' not in body or body['object'] != 'whatsapp_business_account':
            logger.warning("Invalid webhook payload received")
            return {"success": False, "error": "Invalid payload format"}
        
        # Extract entry data
        entry = body.get('entry', [])
        if not entry:
            return {"success": False, "error": "No entry data in payload"}
        
        # Process all incoming messages
        for entry_item in entry:
            # Get the WhatsApp Business Account ID for verification
            whatsapp_business_id = entry_item.get('id')
            if whatsapp_business_id != settings.whatsapp_business_account_id:
                logger.warning(f"Mismatched business account ID: {whatsapp_business_id}")
                continue
                
            # Process all changes in this entry
            changes = entry_item.get('changes', [])
            for change in changes:
                if change.get('field') != 'messages':
                    continue
                    
                # Get the messages from this change
                value = change.get('value', {})
                messages = value.get('messages', [])
                
                for message in messages:
                    # Process each message
                    process_whatsapp_message(message, settings)
                    
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

def process_whatsapp_message(message, settings):
    """
    Process an individual WhatsApp message.
    
    Args:
        message: The WhatsApp message object
        settings: Application settings
        
    Returns:
        None
    """
    try:
        # Extract message information
        message_id = message.get('id')
        message_type = message.get('type')
        sender_id = message.get('from')
        timestamp = message.get('timestamp')
        
        # Log the receipt of message
        logger.info(f"Processing message from {sender_id}, type: {message_type}, id: {message_id}")
        
        # Handle different message types
        if message_type == 'text':
            text_data = message.get('text', {})
            text_body = text_data.get('body', '')
            
            # TODO: Implement text message handling
            logger.info(f"Received text message: {text_body}")
            
            # Here you would add the logic to:
            # 1. Extract billing information from the message
            # 2. Process it with AI (OpenAI)
            # 3. Store in Firestore
            # 4. Respond to the user
            
        elif message_type == 'image':
            # Extract image details
            image_data = message.get('image', {})
            image_id = image_data.get('id', '')
            image_mime = image_data.get('mime_type', '')
            image_caption = image_data.get('caption', '')
            
            logger.info(f"Received image message: ID={image_id}, MIME={image_mime}")
            
            # Download the image using the WhatsApp API
            file_path = download_whatsapp_media(image_id, 'image', sender_id, settings)
            
            if file_path:
                logger.info(f"Successfully downloaded image to: {file_path}")
                
                # Process the image for bill information
                try:
                    from app.utils.document_processor import \
                        extract_text_from_image

                    # Extract text from the image
                    extracted_text = extract_text_from_image(file_path)
                    
                    if extracted_text:
                        logger.info(f"Extracted text from image: {extracted_text[:100]}...")
                        
                        # Send initial confirmation to user
                        send_whatsapp_message(
                            sender_id,
                            "I've received your bill image and am analyzing it now. This will take a few moments...",
                            settings
                        )
                        
                        # Analyze the text with OpenAI to extract bill information
                        bill_data = analyze_text_with_openai(extracted_text, 'bill', settings)
                        
                        if bill_data:
                            # Generate a human-readable summary
                            summary = generate_bill_summary(bill_data)
                            
                            # Send the summary to the user
                            send_whatsapp_message(sender_id, summary, settings)
                            
                            # TODO: Store the bill data in Firestore
                            # store_bill_data(bill_data, sender_id, settings)
                        else:
                            logger.warning("Failed to analyze bill information from image text")
                            send_whatsapp_message(
                                sender_id,
                                "I was able to read your image but couldn't identify bill information. Please ensure this is a bill or receipt image.",
                                settings
                            )
                    else:
                        logger.warning("Failed to extract text from image")
                        send_whatsapp_message(
                            sender_id,
                            "I received your image but couldn't read any text from it. Please ensure the image is clear and try again.",
                            settings
                        )
                        
                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
                    send_whatsapp_message(
                        sender_id,
                        "I had trouble processing your image. Please try again or send the bill information in a different format.",
                        settings
                    )
            else:
                logger.error(f"Failed to download image: {image_id}")
                error_msg = "I had trouble downloading your image. This might be due to an authentication issue with the WhatsApp API. Please try again later or contact support."
                try:
                    send_whatsapp_message(sender_id, error_msg, settings)
                except Exception as e:
                    logger.error(f"Failed to send error message: {str(e)}")
                    logger.error("This is likely due to an invalid or expired WhatsApp API token")
            
        elif message_type == 'document':
            # Extract document details
            document_data = message.get('document', {})
            document_caption = document_data.get('caption', '')
            document_filename = document_data.get('filename', '')
            document_mime = document_data.get('mime_type', '')
            document_id = document_data.get('id', '')
            document_hash = document_data.get('sha256', '')
            
            logger.info(f"Received document: {document_filename} ({document_mime}), ID={document_id}")
            
            # Download the document using WhatsApp API
            file_path = download_whatsapp_media(document_id, 'document', sender_id, settings)
            
            if file_path:
                # Process based on document type
                if document_mime == 'application/pdf':
                    # Process PDF document (e.g., extract bill information)
                    bill_data = process_pdf_document(file_path, sender_id, settings)
                    
                    # Send a response back to the user
                    if bill_data.get("processed", False):
                        response_msg = "I've received your PDF document and processed it."
                        # You could add more details from the processed data here
                    else:
                        response_msg = "I received your document but had trouble processing it."
                    
                    send_whatsapp_message(sender_id, response_msg, settings)
                    
                elif document_mime in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                    # Process Excel document
                    bill_data = process_excel_document(file_path, sender_id, settings)
                    
                    # Send a response back to the user
                    if bill_data.get("processed", False):
                        response_msg = "I've received your Excel document and processed it."
                    else:
                        response_msg = "I received your document but had trouble processing it."
                        
                    send_whatsapp_message(sender_id, response_msg, settings)
                    
                else:
                    # Handle other document types
                    logger.info(f"Unsupported document type: {document_mime}")
                    send_whatsapp_message(
                        sender_id, 
                        f"I received your document ({document_filename}) but I don't know how to process this type of file yet.",
                        settings
                    )
            else:
                logger.error(f"Failed to download document: {document_id}")
                send_whatsapp_message(
                    sender_id,
                    "I had trouble downloading your document. Please try sending it again.",
                    settings
                )
            
        elif message_type == 'audio':
            # TODO: Implement audio message handling
            audio_data = message.get('audio', {})
            audio_id = audio_data.get('id', '')
            audio_mime = audio_data.get('mime_type', '')
            
            logger.info(f"Received audio message: ID={audio_id}, MIME={audio_mime}")
            
            # TODO: Download and process audio
            # download_whatsapp_media(audio_id, 'audio', sender_id, settings)
            
        elif message_type == 'location':
            # TODO: Implement location message handling
            location_data = message.get('location', {})
            latitude = location_data.get('latitude', '')
            longitude = location_data.get('longitude', '')
            address = location_data.get('address', '')
            name = location_data.get('name', '')
            
            logger.info(f"Received location: {name} {address}, lat={latitude}, long={longitude}")
            
            # TODO: Process location data (e.g., find nearby merchants)
            
        elif message_type == 'button':
            # TODO: Implement button response handling
            button_data = message.get('button', {})
            button_text = button_data.get('text', '')
            logger.info(f"Received button response: {button_text}")
            
            # TODO: Process button click based on button text
            
        elif message_type == 'interactive':
            # TODO: Implement interactive message handling
            interactive_data = message.get('interactive', {})
            interactive_type = interactive_data.get('type', '')
            
            if interactive_type == 'button_reply':
                button_reply = interactive_data.get('button_reply', {})
                button_id = button_reply.get('id', '')
                button_title = button_reply.get('title', '')
                logger.info(f"Received interactive button reply: {button_title} (ID: {button_id})")
                
                # TODO: Process button reply based on button ID
                
            elif interactive_type == 'list_reply':
                list_reply = interactive_data.get('list_reply', {})
                list_id = list_reply.get('id', '')
                list_title = list_reply.get('title', '')
                logger.info(f"Received interactive list reply: {list_title} (ID: {list_id})")
                
                # TODO: Process list selection based on list ID
                
            else:
                logger.info(f"Received unsupported interactive message type: {interactive_type}")
            
        else:
            logger.info(f"Received unsupported message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

# Main entry point for running the app directly
if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
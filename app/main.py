"""
WhatsApp Billing Bot - Main Application Entry Point

This module initializes the FastAPI application and includes all the routes
for the application. It serves as the entry point for the WhatsApp billing bot.
"""

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import uvicorn
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from jwt import ExpiredSignatureError

from app.api.admin.admin import router as admin_router
from app.config import Settings, get_settings
from app.services.ai_service import analyze_text_with_openai, generate_bill_summary
from app.services.firebase_chat_history import FirebaseChatHistory
from app.services.llm_service import llm_service
from app.services.processed_messages import check_message_status_and_save
from app.utils.background_job import DocumentJob, process_document
from app.utils.document_processor import extract_text_from_image
from app.utils.global_logging import get_logger
from app.utils.llm_tools import run_llm_tools
from app.utils.types import LLMResponse  # Import the LLMResponse type
from app.utils.whatsapp import (
    check_whatsapp_token,
    download_whatsapp_media,
    send_read_receipt,
    send_typing_indicator,
    send_whatsapp_message,
)

settings = get_settings()


logger = get_logger(__name__)
logger.info(f"Starting application with log level: {settings.log_level}")

# Validate WhatsApp API token
token_valid = check_whatsapp_token(settings)
if not token_valid:
    logger.warning(
        "WhatsApp API token validation failed. Some functionality may not work."
    )

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp Billing Bot API",
    description="API for WhatsApp billing automation with AI capabilities",
    version="1.0.0",
)

# Get the project root directory (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"

app.add_middleware(
    # Configure CORS
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include admin router
app.include_router(admin_router)


# Handle expired JWT tokens globally
@app.exception_handler(ExpiredSignatureError)
async def expired_token_exception_handler(request, exc):
    logger.warning("Expired token used")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
    )


# Handle general exceptions globally
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An internal server error occurred",
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
        "environment": settings.environment,
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
        "health": "/health",
    }


# WhatsApp webhook verification endpoint
@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(
    request: Request, settings: Settings = Depends(get_settings)
):
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
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
):
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
        # print(f"Received webhook: {json.dumps(body, indent=2)}")
        # Log the incoming request for debugging

        # Check if this is a valid WhatsApp message
        if "object" not in body or body["object"] != "whatsapp_business_account":
            logger.warning("Invalid webhook payload received")
            return {"success": False, "error": "Invalid payload format"}

        # Extract entry data
        entry = body.get("entry", [])
        if not entry:
            return {"success": False, "error": "No entry data in payload"}

        # Process all incoming messages
        for entry_item in entry:
            # Get the WhatsApp Business Account ID for verification
            whatsapp_business_id = entry_item.get("id")
            if whatsapp_business_id != settings.whatsapp_business_account_id:
                logger.warning(
                    f"Mismatched business account ID: {whatsapp_business_id}"
                )
                continue

            # Process all changes in this entry
            changes = entry_item.get("changes", [])
            for change in changes:
                if change.get("field") != "messages":
                    continue

                # Get the messages from this change
                value = change.get("value", {})
                messages = value.get("messages", [])

                for message in messages:
                    # Process each message
                    process_whatsapp_message(message, settings, background_tasks)

        return {"success": True}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}",
        )


def process_whatsapp_message(
    message, settings, background_tasks: BackgroundTasks = None
):
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
        message_id = message.get("id")
        message_type = message.get("type")
        sender_id = message.get("from")
        # Check if message is already processed
        if check_message_status_and_save(message_id):
            logger.warning(f"Message {message_id} is already processed.")
            return
        #  Send typing indicator
        send_read_receipt(message_id)
        send_typing_indicator(message_id)
        chat_history = FirebaseChatHistory(sender_id)
        # Log the receipt of message
        logger.info(
            f"Processing message from {sender_id}, type: {message_type}, id: {message_id}"
        )

        # Handle different message types
        if message_type == "text":
            try:
                text_data = message.get("text", {})
                text_body = text_data.get("body", "")

                logger.info(f"Received text message: {text_body}")

                chat_history.add_human_message(text_body, message_id)
                # TODO: update llm service to access chat history
                # TODO: limit maximum iterations to avoid infinite loops
                while True:
                    resp: LLMResponse = llm_service.format_and_query(
                        chat_history.messages
                    )

                    if resp["type"] == "tool_calls":
                        chat_history.add_ai_message("", resp["tool_calls"])
                        chat_history = run_llm_tools(
                            resp["tool_calls"], chat_history, sender_id
                        )
                    elif resp["type"] == "message":
                        chat_history.add_ai_message(resp["text"])
                        break

                logger.info(f"LLM response: {resp}")
                chat_history.commit()
                return send_whatsapp_message(sender_id, f"{resp['text']}", settings)
            except Exception as e:
                logger.error(f"Something went wrong: {e}")
        elif message_type == "image":
            # Extract image details
            image_data = message.get("image", {})
            image_id = image_data.get("id", "")
            image_mime = image_data.get("mime_type", "")
            image_caption = image_data.get("caption", "")

            logger.info(f"Received image message: ID={image_id}, MIME={image_mime}")

            # Download the image using the WhatsApp API
            file_path = download_whatsapp_media(image_id, "image", sender_id, settings)

            if file_path:
                logger.info(f"Successfully downloaded image to: {file_path}")

                # Process the image for bill information
                try:
                    # Extract text from the image
                    extracted_text = extract_text_from_image(file_path)

                    if extracted_text:
                        logger.info(
                            f"Extracted text from image: {extracted_text[:100]}..."
                        )

                        # Send initial confirmation to user
                        send_whatsapp_message(
                            sender_id,
                            "I've received your bill image and am analyzing it now. This will take a few moments...",
                            settings,
                        )

                        # Analyze the text with OpenAI to extract bill information
                        bill_data = analyze_text_with_openai(
                            extracted_text, "bill", settings
                        )

                        if bill_data:
                            # Generate a human-readable summary
                            summary = generate_bill_summary(bill_data)

                            # Send the summary to the user
                            send_whatsapp_message(sender_id, summary, settings)

                            # TODO: Store the bill data in Firestore
                            # store_bill_data(bill_data, sender_id, settings)
                        else:
                            logger.warning(
                                "Failed to analyze bill information from image text"
                            )
                            send_whatsapp_message(
                                sender_id,
                                "I was able to read your image but couldn't identify bill information. Please ensure this is a bill or receipt image.",
                                settings,
                            )
                    else:
                        logger.warning("Failed to extract text from image")
                        send_whatsapp_message(
                            sender_id,
                            "I received your image but couldn't read any text from it. Please ensure the image is clear and try again.",
                            settings,
                        )

                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
                    send_whatsapp_message(
                        sender_id,
                        "I had trouble processing your image. Please try again or send the bill information in a different format.",
                        settings,
                    )
            else:
                logger.error(f"Failed to download image: {image_id}")
                error_msg = "I had trouble downloading your image. This might be due to an authentication issue with the WhatsApp API. Please try again later or contact support."
                try:
                    send_whatsapp_message(sender_id, error_msg, settings)
                except Exception as e:
                    logger.error(f"Failed to send error message: {str(e)}")
                    logger.error(
                        "This is likely due to an invalid or expired WhatsApp API token"
                    )

        elif message_type == "document":
            # Extract document details
            document_data = message.get("document", {})
            document_caption = document_data.get("caption", "")
            document_filename = document_data.get("filename", "")
            document_mime = document_data.get("mime_type", "")
            document_id = document_data.get("id", "")
            document_hash = document_data.get("sha256", "")

            document_job: DocumentJob = DocumentJob(
                sender_id=sender_id,
                type="document",
                whatsapp_id=sender_id,
                doc_caption=document_caption,
                doc_filename=document_filename,
                doc_mime=document_mime,
                doc_id=document_id,
                doc_hash=document_hash,
            )

            if background_tasks:
                logger.info("Adding to background task queue")
                background_tasks.add_task(process_document, document_job)

        elif message_type == "audio":
            # TODO: Implement audio message handling
            audio_data = message.get("audio", {})
            audio_id = audio_data.get("id", "")
            audio_mime = audio_data.get("mime_type", "")

            logger.info(f"Received audio message: ID={audio_id}, MIME={audio_mime}")

            # TODO: Download and process audio
            # download_whatsapp_media(audio_id, 'audio', sender_id, settings)

        elif message_type == "location":
            # TODO: Implement location message handling
            location_data = message.get("location", {})
            latitude = location_data.get("latitude", "")
            longitude = location_data.get("longitude", "")
            address = location_data.get("address", "")
            name = location_data.get("name", "")

            logger.info(
                f"Received location: {name} {address}, lat={latitude}, long={longitude}"
            )

            # TODO: Process location data (e.g., find nearby merchants)

        elif message_type == "button":
            # TODO: Implement button response handling
            button_data = message.get("button", {})
            button_text = button_data.get("text", "")
            logger.info(f"Received button response: {button_text}")

            # TODO: Process button click based on button text

        elif message_type == "interactive":
            # TODO: Implement interactive message handling
            interactive_data = message.get("interactive", {})
            interactive_type = interactive_data.get("type", "")

            if interactive_type == "button_reply":
                button_reply = interactive_data.get("button_reply", {})
                button_id = button_reply.get("id", "")
                button_title = button_reply.get("title", "")
                logger.info(
                    f"Received interactive button reply: {button_title} (ID: {button_id})"
                )

                # TODO: Process button reply based on button ID

            elif interactive_type == "list_reply":
                list_reply = interactive_data.get("list_reply", {})
                list_id = list_reply.get("id", "")
                list_title = list_reply.get("title", "")
                logger.info(
                    f"Received interactive list reply: {list_title} (ID: {list_id})"
                )

                # TODO: Process list selection based on list ID

            else:
                logger.info(
                    f"Received unsupported interactive message type: {interactive_type}"
                )

        else:
            logger.info(f"Received unsupported message type: {message_type}")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")


# React admin app
@app.get("/admin/*", response_class=FileResponse)
async def get_admin_app():
    return FileResponse(str(DIST_DIR / "index.html"))


# Mount static files for serving React app assets
# These must be mounted after all API routes to avoid conflicts
@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    """Serve static assets from the dist/assets directory"""
    asset_path = DIST_DIR / "assets" / file_path
    if asset_path.exists() and asset_path.is_file():
        # Set proper media type based on file extension
        media_type = None
        if file_path.endswith(".js"):
            media_type = "application/javascript"
        elif file_path.endswith(".css"):
            media_type = "text/css"
        elif file_path.endswith(".svg"):
            media_type = "image/svg+xml"
        return FileResponse(str(asset_path), media_type=media_type)
    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/vite.svg")
async def serve_vite_svg():
    """Serve the vite.svg file"""
    svg_path = DIST_DIR / "vite.svg"
    if svg_path.exists():
        return FileResponse(str(svg_path), media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="File not found")


# Main entry point for running the app directly
if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

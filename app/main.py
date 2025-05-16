"""
WhatsApp Billing Bot - Main Application Entry Point

This module initializes the FastAPI application and includes all the routes
for the application. It serves as the entry point for the WhatsApp billing bot.
"""

import logging
import os
from datetime import UTC, datetime

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings

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

# Main entry point for running the app directly
if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
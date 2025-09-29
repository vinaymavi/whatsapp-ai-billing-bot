"""
Pytest configuration file.

This file contains pytest fixtures and configuration settings.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    Create a FastAPI TestClient as a fixture.

    Returns:
        TestClient: A test client for FastAPI application
    """
    return TestClient(app)

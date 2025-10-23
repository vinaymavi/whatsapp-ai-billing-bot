"""
Tests for the main application endpoints.
"""


def test_health_endpoint(client):
    """Test that the health endpoint returns a 200 status code and expected fields."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(client):
    """Test that the root endpoint returns a 200 status code and expected message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "documentation" in data
    assert "health" in data


def test_global_exception_middleware(client):
    """
    Test that the global exception middleware catches unhandled exceptions gracefully.

    This test verifies that:
    1. The middleware catches exceptions that aren't handled by specific handlers
    2. Returns a 500 status code
    3. Returns JSON with error details
    4. Includes the exception type in the response
    """
    # The test endpoint that intentionally raises an exception
    response = client.get("/test-exception")

    # Should return 500 Internal Server Error
    assert response.status_code == 500

    # Should return JSON response
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "An internal server error occurred"
    assert "error_type" in data

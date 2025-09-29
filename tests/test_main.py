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

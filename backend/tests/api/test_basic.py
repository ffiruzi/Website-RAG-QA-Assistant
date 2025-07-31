def test_health_check(client):
    """Test that the health check endpoint is working."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_exists(client):
    """Test that the API router is registered."""
    response = client.get("/api/v1")
    # Should get a 404 because /api/v1 doesn't exist, but not a 500
    assert response.status_code == 404

    # Try to get the OpenAPI schema which should exist
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200


def test_websites_endpoint_exists(client):
    """Test that the websites endpoint exists."""
    # This should give a 401 Unauthorized, not a 404 Not Found
    response = client.get("/api/v1/websites/")
    assert response.status_code == 401, "Websites endpoint not found or not protected"
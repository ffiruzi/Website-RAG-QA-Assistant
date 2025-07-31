import pytest
from fastapi.testclient import TestClient
import logging

logger = logging.getLogger(__name__)


def test_create_website(client, superuser_token_headers):
    """Test creating a website."""
    # Test creating a website with valid data
    website_data = {
        "url": "https://example.com",
        "name": "Example Website",
        "description": "This is an example website",
        "is_active": True,
        "sitemap_url": "https://example.com/sitemap.xml"
    }

    response = client.post(
        "/api/v1/websites/",
        json=website_data,
        headers=superuser_token_headers
    )

    logger.info(f"Create website response: {response.status_code} - {response.text}")

    assert response.status_code == 201
    data = response.json()
    assert data["url"] == website_data["url"]
    assert data["name"] == website_data["name"]
    assert "id" in data

    # Test creating a website with duplicate URL
    response = client.post(
        "/api/v1/websites/",
        json=website_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 400

    # Test creating a website with invalid URL
    website_data["url"] = "invalid-url"
    response = client.post(
        "/api/v1/websites/",
        json=website_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 422  # Validation error

    # Test creating a website without authentication
    website_data["url"] = "https://example2.com"
    response = client.post("/api/v1/websites/", json=website_data)
    assert response.status_code == 401  # Unauthorized


def test_read_websites(client, superuser_token_headers, normal_user_token_headers):
    """Test reading websites."""
    # Create a test website
    website_data = {
        "url": "https://example.com",
        "name": "Example Website"
    }
    client.post(
        "/api/v1/websites/",
        json=website_data,
        headers=superuser_token_headers
    )

    # Test getting all websites as superuser
    response = client.get("/api/v1/websites/", headers=superuser_token_headers)
    logger.info(f"Read websites response: {response.status_code} - {response.text}")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["items"][0]["url"] == website_data["url"]

    # Test getting all websites as normal user
    response = client.get("/api/v1/websites/", headers=normal_user_token_headers)
    assert response.status_code == 200

    # Test getting all websites without authentication
    response = client.get("/api/v1/websites/")
    assert response.status_code == 401  # Unauthorized

    # Test pagination
    response = client.get(
        "/api/v1/websites/?page=1&page_size=10",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["page"] == 1
    assert response.json()["page_size"] == 10


def test_read_website(client, superuser_token_headers):
    """Test reading a single website."""
    # Create a test website
    website_data = {
        "url": "https://example.com",
        "name": "Example Website"
    }
    create_response = client.post(
        "/api/v1/websites/",
        json=website_data,
        headers=superuser_token_headers
    )
    website_id = create_response.json()["id"]

    # Test getting a specific website
    response = client.get(f"/api/v1/websites/{website_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == website_data["url"]
    assert data["name"] == website_data["name"]

    # Test getting a non-existent website
    response = client.get("/api/v1/websites/999", headers=superuser_token_headers)
    assert response.status_code == 404


def test_update_website(client, superuser_token_headers):
    """Test updating a website."""
    # Create a test website
    website_data = {
        "url": "https://example.com",
        "name": "Example Website"
    }
    create_response = client.post(
        "/api/v1/websites/",
        json=website_data,
        headers=superuser_token_headers
    )
    website_id = create_response.json()["id"]

    # Test updating a website
    update_data = {
        "name": "Updated Website",
        "description": "Updated description"
    }
    response = client.put(
        f"/api/v1/websites/{website_id}",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    # URL should remain unchanged
    assert data["url"] == website_data["url"]

    # Test updating a non-existent website
    response = client.put(
        "/api/v1/websites/999",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 404


def test_delete_website(client, superuser_token_headers):
    """Test deleting a website."""
    # Create a test website
    website_data = {
        "url": "https://example.com",
        "name": "Example Website"
    }
    create_response = client.post(
        "/api/v1/websites/",
        json=website_data,
        headers=superuser_token_headers
    )
    website_id = create_response.json()["id"]

    # Test deleting a website
    response = client.delete(
        f"/api/v1/websites/{website_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 204

    # Verify website was deleted
    response = client.get(
        f"/api/v1/websites/{website_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

    # Test deleting a non-existent website
    response = client.delete(
        "/api/v1/websites/999",
        headers=superuser_token_headers
    )
    assert response.status_code == 404
import logging
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User

logger = logging.getLogger(__name__)


def test_login(client, test_db):
    """Test login endpoint with explicit user creation."""
    # Create user credentials
    test_email = "logintest@example.com"
    test_password = "loginpassword"

    # Create a test user directly in the database
    test_user = User(
        email=test_email,
        hashed_password=get_password_hash(test_password),
        full_name="Login Test User",
        is_active=True,
        is_superuser=True
    )

    # Add and commit to the database
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    logger.info(f"Created login test user: {test_user.email} with ID: {test_user.id}")

    # Create login data
    login_data = {
        "username": test_email,
        "password": test_password,
    }

    # Attempt login
    response = client.post("/api/v1/auth/login", data=login_data)
    logger.info(f"Login response: {response.status_code} - {response.text}")

    # Check response
    assert response.status_code == 200, f"Login failed: {response.text}"
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Test login with incorrect password
    login_data = {
        "username": test_email,
        "password": "wrong_password",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 400

    # Test login with non-existent user
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 400
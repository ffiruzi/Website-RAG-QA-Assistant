import logging
from fastapi.testclient import TestClient
from app.core.security import get_password_hash
from app.models.user import User

logger = logging.getLogger(__name__)


def test_auth_login_debug(client, test_db):
    """Debug the auth login endpoint with detailed logging."""
    # Create a test user directly in the database
    test_email = "debug@example.com"
    test_password = "debugpassword"

    # Create a hashed password
    hashed_password = get_password_hash(test_password)
    logger.info(f"Created password hash: {hashed_password[:10]}...")

    # Create a user
    test_user = User(
        email=test_email,
        hashed_password=hashed_password,
        full_name="Debug User",
        is_active=True,
        is_superuser=True
    )
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    logger.info(f"Created debug user: {test_user.email} with ID: {test_user.id}")

    # Attempt to login
    login_data = {
        "username": test_email,
        "password": test_password
    }

    # Log the data being sent
    logger.info(f"Attempting login with data: {login_data}")

    # Try with both data and json to see if there's a difference
    response_data = client.post("/api/v1/auth/login", data=login_data)
    logger.info(f"Login response (data): {response_data.status_code} - {response_data.text}")

    # Add more debug info to help diagnose the issue
    if response_data.status_code != 200:
        # Check if the user exists in the database
        user = test_db.query(User).filter(User.email == test_email).first()
        logger.info(f"User exists in DB: {user is not None}")
        if user:
            logger.info(f"User DB info - ID: {user.id}, Email: {user.email}, Active: {user.is_active}")
            logger.info(f"Stored hash: {user.hashed_password[:10]}...")

    # Assert results
    assert response_data.status_code == 200, f"Login failed: {response_data.text}"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys
import logging
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import get_db, Base
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.core.config import settings

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Test user credentials
TEST_USER_EMAIL = "admin@example.com"
TEST_USER_PASSWORD = "password"
TEST_NORMAL_USER_EMAIL = "user@example.com"
TEST_NORMAL_USER_PASSWORD = "password"


@pytest.fixture(scope="function")
def test_db():
    """Create a clean test database with test users for each test."""
    # Drop all tables if they exist
    Base.metadata.drop_all(bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()

    try:
        # Create a consistent password hash
        password_hash = get_password_hash(TEST_USER_PASSWORD)
        logger.info(f"Created hashed_password: {password_hash[:10]}...")

        # Add test data - create a test superuser
        test_user = User(
            email=TEST_USER_EMAIL,
            hashed_password=password_hash,
            full_name="Test Admin",
            is_active=True,
            is_superuser=True
        )
        db.add(test_user)

        # Create regular user
        normal_user = User(
            email=TEST_NORMAL_USER_EMAIL,
            hashed_password=password_hash,  # Use same hash for simplicity
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        db.add(normal_user)

        # Commit both users
        db.commit()

        # Refresh to get IDs
        db.refresh(test_user)
        db.refresh(normal_user)

        logger.info(f"Created test user: {test_user.email} - ID: {test_user.id}")
        logger.info(f"Created normal user: {normal_user.email} - ID: {normal_user.id}")

        yield db
    except Exception as e:
        logger.error(f"Error in test_db fixture: {str(e)}")
        db.rollback()
        raise
    finally:
        # Close session
        db.close()


@pytest.fixture
def client(test_db):
    # Create a test client using the testing database
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_tokens(client):
    """Get actual tokens by logging in."""
    # Login as admin
    admin_login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    response = client.post("/api/v1/auth/login", data=admin_login_data)
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    admin_token = response.json()["access_token"]

    # Login as normal user
    user_login_data = {
        "username": TEST_NORMAL_USER_EMAIL,
        "password": TEST_NORMAL_USER_PASSWORD
    }
    response = client.post("/api/v1/auth/login", data=user_login_data)
    assert response.status_code == 200, f"User login failed: {response.text}"
    user_token = response.json()["access_token"]

    return {
        "admin": admin_token,
        "user": user_token
    }


@pytest.fixture
def superuser_token_headers(auth_tokens):
    """Get admin token headers."""
    return {"Authorization": f"Bearer {auth_tokens['admin']}"}


@pytest.fixture
def normal_user_token_headers(auth_tokens):
    """Get normal user token headers."""
    return {"Authorization": f"Bearer {auth_tokens['user']}"}
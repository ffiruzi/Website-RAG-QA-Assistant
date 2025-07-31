import logging
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.security import get_password_hash
from app.models.user import User
from app.core.database import Base, get_db
from app.main import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create in-memory SQLite database for this test
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


def test_login_debug():
    """Debug the login functionality."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create a session and add a test user
    db = TestingSessionLocal()

    try:
        # Create test user with plain password
        plain_password = "testpassword"
        hashed_password = get_password_hash(plain_password)

        logger.info(f"Created password hash: {hashed_password}")

        test_user = User(
            email="test@example.com",
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True,
            is_superuser=True
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        logger.info(f"Created test user ID: {test_user.id}")

        # Create test client
        client = TestClient(app)

        # Attempt to login
        login_data = {
            "username": "test@example.com",
            "password": plain_password
        }

        response = client.post("/api/v1/auth/login", data=login_data)
        logger.info(f"Login response: {response.status_code} - {response.text}")

        # Clean up
        Base.metadata.drop_all(bind=engine)

        # Assert result
        assert response.status_code == 200, f"Login failed: {response.text}"
        assert "access_token" in response.json()

    except Exception as e:
        logger.error(f"Test error: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
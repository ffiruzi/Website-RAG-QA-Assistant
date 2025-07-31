import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.models.base import Base
from app.models.user import User
from app.core.security import get_password_hash, verify_password

# Create a new in-memory database for this test
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def main():
    """Simple test to create a user and verify password."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a session
    db = SessionLocal()

    try:
        # Create a test user
        test_email = "test@example.com"
        test_password = "password123"

        # Hash the password
        password_hash = get_password_hash(test_password)
        logger.info(f"Password hash: {password_hash}")

        # Create and save the user
        user = User(
            email=test_email,
            hashed_password=password_hash,
            full_name="Test User",
            is_active=True,
            is_superuser=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created user with ID: {user.id}")

        # Retrieve the user
        retrieved_user = db.query(User).filter(User.email == test_email).first()

        if retrieved_user:
            logger.info(f"Retrieved user: {retrieved_user.email} (ID: {retrieved_user.id})")

            # Verify password
            is_valid = verify_password(test_password, retrieved_user.hashed_password)
            logger.info(f"Password verification: {is_valid}")

            # Try with an incorrect password
            is_invalid = verify_password("wrong_password", retrieved_user.hashed_password)
            logger.info(f"Incorrect password verification: {is_invalid}")

            assert is_valid, "Password verification failed"
            assert not is_invalid, "Invalid password verification succeeded"

            logger.info("Authentication test passed!")
        else:
            logger.error("User not found in database")

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()
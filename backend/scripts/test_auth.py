# scripts/test_auth.py
import logging
import sys
import os
from sqlalchemy.orm import Session

# Add the project root directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add necessary imports
from app.core.database import get_db, Base, engine
from app.models.user import User
from app.core.security import get_password_hash, verify_password


def main():
    """Test authentication directly."""
    # Reset database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Get DB session
    session = next(get_db())

    try:
        # Create test user
        test_email = "direct@example.com"
        test_password = "directpassword"

        hashed_password = get_password_hash(test_password)
        logger.info(f"Hashed password: {hashed_password}")

        # Create user
        test_user = User(
            email=test_email,
            hashed_password=hashed_password,
            full_name="Direct Test User",
            is_active=True,
            is_superuser=True
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        logger.info(f"Created user with ID: {test_user.id}")

        # Verify user exists in DB
        db_user = session.query(User).filter(User.email == test_email).first()
        logger.info(f"User exists in DB: {db_user is not None}")
        if db_user:
            logger.info(f"DB user ID: {db_user.id}, email: {db_user.email}")

        # Test password verification
        is_valid = verify_password(test_password, db_user.hashed_password)
        logger.info(f"Password verification: {is_valid}")

        invalid_test = verify_password("wrongpassword", db_user.hashed_password)
        logger.info(f"Invalid password verification: {invalid_test}")

        logger.info("Auth test completed successfully!")
    except Exception as e:
        logger.error(f"Error in auth test: {str(e)}", exc_info=True)
    finally:
        session.close()


if __name__ == "__main__":
    main()
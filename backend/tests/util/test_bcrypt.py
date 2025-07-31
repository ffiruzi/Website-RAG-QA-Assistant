import logging
from app.core.security import get_password_hash, verify_password

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_bcrypt():
    """Test if bcrypt password hashing is working."""
    password = "testpassword"

    # Hash the password
    hashed = get_password_hash(password)
    logger.info(f"Password: {password}")
    logger.info(f"Hashed: {hashed}")

    # Verify the password
    is_valid = verify_password(password, hashed)
    logger.info(f"Password valid: {is_valid}")

    assert is_valid, "Password verification failed"

    # Verify a wrong password
    is_valid = verify_password("wrongpassword", hashed)
    logger.info(f"Wrong password valid: {is_valid}")

    assert not is_valid, "Wrong password verification passed incorrectly"


if __name__ == "__main__":
    # Run the test
    test_bcrypt()
    print("Bcrypt test completed successfully")
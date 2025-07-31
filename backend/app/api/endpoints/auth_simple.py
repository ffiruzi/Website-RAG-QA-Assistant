from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
def login_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> Any:
    """Simple login endpoint for debugging."""
    try:
        logger.info(f"Login attempt for {form_data.username}")

        # Get user directly from database
        user = db.query(User).filter(User.email == form_data.username).first()

        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )

        # Check password
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=user.email,
            expires_delta=access_token_expires,
            scopes=["admin"] if user.is_superuser else ["user"]
        )

        logger.info(f"Login successful for {form_data.username}")

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import Token
from datetime import timedelta

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # In development mode, always return a token
    if settings.ENVIRONMENT == "development" and settings.DEBUG:
        # Create a default admin user if it doesn't exist
        repository = UserRepository(db)
        user = repository.get_by_email("admin@example.com")

        if not user:
            from app.core.security import get_password_hash
            user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("password"),
                full_name="Admin User",
                is_active=True,
                is_superuser=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create token with long expiry
        access_token_expires = timedelta(days=30)
        token = create_access_token(
            subject=user.email,
            expires_delta=access_token_expires,
            scopes=["admin"]
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    # Normal authentication flow for production
    repository = UserRepository(db)
    user = repository.get_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires,
        scopes=["admin"] if user.is_superuser else ["user"],
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/token", response_model=Token)
def get_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Get a token using username and password.
    This is the same as the login endpoint.
    """
    return login_for_access_token(form_data, db)
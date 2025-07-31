from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Generator, List, Optional, Dict, Any, TypeVar, Generic, Type
from pydantic import BaseModel
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.database import get_db
from app.repositories.website import WebsiteRepository
from app.models.user import User
from app.schemas.user import TokenPayload
from app.core.config import settings
from app.repositories.user import UserRepository

T = TypeVar('T')


class PaginationParams:
    def __init__(
            self,
            page: int = Query(1, ge=1, description="Page number"),
            page_size: int = Query(20, ge=1, le=100, description="Items per page"),
            sort_by: Optional[str] = Query(None, description="Sort field"),
            sort_order: str = Query("asc", description="Sort order")
    ):
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()
        self.offset = (page - 1) * page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


def get_website_repository(db: Session = Depends(get_db)) -> WebsiteRepository:
    return WebsiteRepository(db)


def get_pagination(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
        sort_by: Optional[str] = Query(None, description="Sort field"),
        sort_order: str = Query("asc", description="Sort order (asc or desc)")
) -> PaginationParams:
    return PaginationParams(page, page_size, sort_by, sort_order)


from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """Get the current user from the token."""
    try:
        # If we're in development mode, don't verify the token
        if settings.ENVIRONMENT == "development" and settings.DEBUG:
            # Create a default user if it doesn't exist
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

            return user

        # Normal token verification
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    repository = UserRepository(db)
    user = repository.get_by_email(token_data.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """Check if the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
        current_user: User = Depends(get_current_user),
) -> User:
    """Check if the current user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
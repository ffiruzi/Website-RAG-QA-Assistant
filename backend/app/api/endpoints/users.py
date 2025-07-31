from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.api.dependencies import get_current_active_superuser, PaginationParams, get_pagination
from app.core.errors import NotFoundError, BadRequestError

router = APIRouter()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.get("/", response_model=List[UserResponse])
def read_users(
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
        repository: UserRepository = Depends(get_user_repository)
):
    """
    Retrieve all users. Only for superusers.
    """
    users = repository.get_all(
        skip=pagination.offset,
        limit=pagination.page_size,
        order_by=pagination.sort_by or "id",
        sort_order=pagination.sort_order
    )
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
        user_in: UserCreate,
        current_user: User = Depends(get_current_active_superuser),
        repository: UserRepository = Depends(get_user_repository)
):
    """
    Create new user. Only for superusers.
    """
    # Check if user with this email already exists
    existing_user = repository.get_by_email(user_in.email)
    if existing_user:
        raise BadRequestError(f"User with email '{user_in.email}' already exists")

    return repository.create(user_in)


@router.get("/me", response_model=UserResponse)
def read_user_me(
        current_user: User = Depends(get_current_active_superuser)
):
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_superuser),
        repository: UserRepository = Depends(get_user_repository)
):
    """
    Update current user.
    """
    return repository.update(current_user.id, user_in)


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
        user_id: int = Path(..., description="The ID of the user to get"),
        current_user: User = Depends(get_current_active_superuser),
        repository: UserRepository = Depends(get_user_repository)
):
    """
    Get a specific user by ID. Only for superusers.
    """
    user = repository.get(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        user_in: UserUpdate,
        user_id: int = Path(..., description="The ID of the user to update"),
        current_user: User = Depends(get_current_active_superuser),
        repository: UserRepository = Depends(get_user_repository)
):
    """
    Update a user. Only for superusers.
    """
    user = repository.get(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # If email is being updated, check if it already exists
    if user_in.email is not None and user_in.email != user.email:
        user_with_email = repository.get_by_email(user_in.email)
        if user_with_email is not None:
            raise BadRequestError(f"User with email '{user_in.email}' already exists")

    return repository.update(user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int = Path(..., description="The ID of the user to delete"),
        current_user: User = Depends(get_current_active_superuser),
        repository: UserRepository = Depends(get_user_repository)
):
    """
    Delete a user. Only for superusers.
    """
    user = repository.get(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    if user.id == current_user.id:
        raise BadRequestError("Users cannot delete themselves")

    repository.delete(user_id)
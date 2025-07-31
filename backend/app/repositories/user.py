from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def create(self, obj_in: UserCreate) -> User:
        """Create a new user."""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in: UserUpdate) -> Optional[User]:
        """Update a user."""
        user = self.get(id)
        if not user:
            return None

        update_data = obj_in.dict(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field in update_data:
            if hasattr(user, field):
                setattr(user, field, update_data[field])

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
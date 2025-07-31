from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedBase
from app.core.security import get_password_hash, verify_password


class User(TimeStampedBase):
    __tablename__ = "users"

    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User {self.email}>"

    @staticmethod
    def get_password_hash(password: str) -> str:
        return get_password_hash(password)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self.hashed_password)
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.schemas.base import TimeStampedSchema


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDB(TimeStampedSchema, UserBase):
    pass


class UserResponse(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # User ID
    exp: datetime
    scopes: list[str] = []
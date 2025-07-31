from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.base import TimeStampedSchema


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: int
    content: str
    is_user_message: bool = True
    sources: Optional[str] = None  # JSON string of source URLs


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: Optional[str] = None
    sources: Optional[str] = None


class MessageInDB(TimeStampedSchema, MessageBase):
    pass


class MessageResponse(MessageInDB):
    pass
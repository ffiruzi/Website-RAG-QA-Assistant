from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.base import TimeStampedSchema


class ConversationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    website_id: int
    session_id: str
    conversation_metadata: Optional[Dict[str, Any]] = None  # Changed from 'metadata' to 'conversation_metadata'


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    website_id: Optional[int] = None
    session_id: Optional[str] = None
    conversation_metadata: Optional[Dict[str, Any]] = None  # Changed from 'metadata' to 'conversation_metadata'


class ConversationInDB(TimeStampedSchema, ConversationBase):
    pass


class ConversationResponse(ConversationInDB):
    pass
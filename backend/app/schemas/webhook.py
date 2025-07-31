from pydantic import BaseModel, field_validator, ConfigDict, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import TimeStampedSchema


class WebhookBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    website_id: int
    name: str
    url: HttpUrl
    secret: Optional[str] = None
    is_active: bool = True
    events: List[str]  # List of events to trigger this webhook


class WebhookCreate(WebhookBase):
    @field_validator('events')
    @classmethod
    def validate_events(cls, v):
        valid_events = [
            'conversation.created',
            'message.created',
            'answer.generated',
            'feedback.received',
            'embedding.completed'
        ]
        for event in v:
            if event not in valid_events:
                raise ValueError(f"Invalid event: {event}")
        return v


class WebhookUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None
    events: Optional[List[str]] = None

    @field_validator('events')
    @classmethod
    def validate_events(cls, v):
        if v is None:
            return v

        valid_events = [
            'conversation.created',
            'message.created',
            'answer.generated',
            'feedback.received',
            'embedding.completed'
        ]
        for event in v:
            if event not in valid_events:
                raise ValueError(f"Invalid event: {event}")
        return v


class WebhookInDB(TimeStampedSchema, WebhookBase):
    pass


class WebhookResponse(WebhookInDB):
    pass


class WebhookLogBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    webhook_id: int
    event: str
    payload: Dict[str, Any]
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None


class WebhookLogCreate(WebhookLogBase):
    pass


class WebhookLogInDB(TimeStampedSchema, WebhookLogBase):
    pass


class WebhookLogResponse(WebhookLogInDB):
    pass
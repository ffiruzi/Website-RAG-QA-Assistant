from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from app.schemas.base import TimeStampedSchema


class PageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    website_id: int
    last_crawled_at: Optional[str] = None
    is_indexed: bool = False


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    website_id: Optional[int] = None
    last_crawled_at: Optional[str] = None
    is_indexed: Optional[bool] = None


class PageInDB(TimeStampedSchema, PageBase):
    pass


class PageResponse(PageInDB):
    pass
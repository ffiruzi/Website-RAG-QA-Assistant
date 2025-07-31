from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from app.schemas.base import TimeStampedSchema
import validators


class WebsiteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    sitemap_url: Optional[str] = None
    prompt_template_id: Optional[str] = None

    @field_validator('url', 'sitemap_url')
    def validate_url(cls, v):
        if v is None:
            return v
        if not validators.url(v):
            raise ValueError('Invalid URL')
        return v


class WebsiteCreate(WebsiteBase):
    pass


class WebsiteUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sitemap_url: Optional[str] = None
    prompt_template_id: Optional[str] = None

    @field_validator('url', 'sitemap_url')
    def validate_url(cls, v):
        if v is None:
            return v
        if not validators.url(v):
            raise ValueError('Invalid URL')
        return v


class WebsiteInDB(TimeStampedSchema, WebsiteBase):
    pass


class WebsiteResponse(WebsiteInDB):
    pass
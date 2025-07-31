from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.base import TimeStampedSchema


class EmbeddingJobBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    website_id: int
    status: str = "pending"
    documents_found: int = 0
    documents_processed: int = 0
    chunks_created: int = 0
    processing_time: float = 0.0
    error: Optional[str] = None
    is_refresh: bool = False
    job_metadata: Optional[Dict[str, Any]] = None


class EmbeddingJobCreate(EmbeddingJobBase):
    pass


class EmbeddingJobUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Optional[str] = None
    documents_found: Optional[int] = None
    documents_processed: Optional[int] = None
    chunks_created: Optional[int] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    job_metadata: Optional[Dict[str, Any]] = None


class EmbeddingJobInDB(TimeStampedSchema, EmbeddingJobBase):
    pass


class EmbeddingJobResponse(EmbeddingJobInDB):
    pass
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.base import TimeStampedSchema


class ChunkBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    page_id: int


class ChunkCreate(ChunkBase):
    pass


class ChunkUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: Optional[str] = None
    page_id: Optional[int] = None


class ChunkInDB(TimeStampedSchema, ChunkBase):
    id: int


class ChunkResponse(ChunkInDB):
    pass
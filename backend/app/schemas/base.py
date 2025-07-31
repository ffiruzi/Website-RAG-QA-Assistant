from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class TimeStampedSchema(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
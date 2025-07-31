from sqlalchemy import Column, Integer, DateTime
from datetime import datetime, timezone
from app.core.database import Base


class TimeStampedBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    # Use timezone-aware objects instead of utcnow()
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
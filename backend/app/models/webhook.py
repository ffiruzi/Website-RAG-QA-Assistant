from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedBase


class Webhook(TimeStampedBase):
    __tablename__ = "webhooks"

    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=True)  # Secret for signing webhook payloads
    is_active = Column(Boolean, default=True)
    events = Column(JSON, nullable=False)  # List of events to trigger this webhook

    # Relationships
    website = relationship("Website", back_populates="webhooks")

    def __repr__(self):
        return f"<Webhook {self.name} for website {self.website_id}>"
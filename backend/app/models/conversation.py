from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedBase


class Conversation(TimeStampedBase):
    __tablename__ = "conversations"

    session_id = Column(String, index=True, nullable=False)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    conversation_metadata = Column(JSON, nullable=True)  # Changed from 'metadata' to 'conversation_metadata'

    # Relationships
    website = relationship("Website", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.id} (session: {self.session_id})>"
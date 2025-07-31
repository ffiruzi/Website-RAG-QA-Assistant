from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from .base import TimeStampedBase

class Website(TimeStampedBase):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    sitemap_url = Column(String, nullable=True)
    prompt_template_id = Column(String, nullable=True)

    # Relationships
    pages = relationship("Page", back_populates="website", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="website", cascade="all, delete-orphan")
    embedding_jobs = relationship("EmbeddingJob", back_populates="website", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="website", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Website {self.name} ({self.url})>"
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import TimeStampedBase

class Page(TimeStampedBase):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    last_crawled_at = Column(String, nullable=True)
    is_indexed = Column(Boolean, default=False)

    # Relationships
    website = relationship("Website", back_populates="pages")
    chunks = relationship("Chunk", back_populates="page", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Page {self.url}>"
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import TimeStampedBase

class Chunk(TimeStampedBase):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    page = relationship("Page", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk {self.id}>"
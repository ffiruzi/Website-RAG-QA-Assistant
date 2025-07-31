from sqlalchemy import Column, String, Text, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.base import TimeStampedBase


class PageChunk(TimeStampedBase):
    __tablename__ = "page_chunks"

    content = Column(Text, nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding_file_path = Column(String, nullable=True)  # Path to the stored embeddings file

    # Relationships
    page = relationship("Page", back_populates="chunks")

    def __repr__(self):
        return f"<PageChunk {self.id} from page {self.page_id}>"
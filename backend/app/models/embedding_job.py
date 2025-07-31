from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedBase


class EmbeddingJob(TimeStampedBase):
    __tablename__ = "embedding_jobs"

    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, running, completed, failed
    documents_found = Column(Integer, default=0)
    documents_processed = Column(Integer, default=0)
    chunks_created = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)  # seconds
    error = Column(String, nullable=True)
    is_refresh = Column(Boolean, default=False)
    job_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to 'job_metadata'

    # Relationships
    website = relationship("Website", back_populates="embedding_jobs")

    def __repr__(self):
        return f"<EmbeddingJob {self.id} for website {self.website_id}>"

    def to_dict(self):
        """Convert job to dictionary for serialization."""
        return {
            "id": self.id,
            "website_id": self.website_id,
            "status": self.status,
            "start_time": self.created_at.isoformat() if self.created_at else None,
            "end_time": self.updated_at.isoformat() if self.updated_at else None,
            "documents_found": self.documents_found,
            "documents_processed": self.documents_processed,
            "chunks_created": self.chunks_created,
            "error": self.error,
            "is_refresh": self.is_refresh,
            "progress": round((self.documents_processed / self.documents_found) * 100,
                              2) if self.documents_found > 0 else 0
        }
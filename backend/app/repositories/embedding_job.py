from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.embedding_job import EmbeddingJob
from app.schemas.embedding_job import EmbeddingJobCreate, EmbeddingJobUpdate
from app.repositories.base import BaseRepository


class EmbeddingJobRepository(BaseRepository[EmbeddingJob, EmbeddingJobCreate, EmbeddingJobUpdate]):
    def __init__(self, db: Session):
        super().__init__(EmbeddingJob, db)

    def get_by_website_id(self, website_id: int) -> List[EmbeddingJob]:
        """Get all embedding jobs for a website."""
        return self.db.query(EmbeddingJob).filter(EmbeddingJob.website_id == website_id).all()

    def get_latest_by_website_id(self, website_id: int) -> Optional[EmbeddingJob]:
        """Get the latest embedding job for a website."""
        return self.db.query(EmbeddingJob).filter(
            EmbeddingJob.website_id == website_id
        ).order_by(EmbeddingJob.created_at.desc()).first()

    def get_running_jobs(self) -> List[EmbeddingJob]:
        """Get all running embedding jobs."""
        return self.db.query(EmbeddingJob).filter(EmbeddingJob.status == "running").all()

    def get_jobs_by_status(self, status: str) -> List[EmbeddingJob]:
        """Get all embedding jobs with a specific status."""
        return self.db.query(EmbeddingJob).filter(EmbeddingJob.status == status).all()
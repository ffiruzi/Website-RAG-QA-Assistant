"""
Local simplified version of the embedding manager to avoid import issues.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
import time
import datetime
import uuid
import os
import json

from app.models.embedding_job import EmbeddingJob
from app.repositories.embedding_job import EmbeddingJobRepository
from app.services.embeddings.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embedding jobs for websites (simplified version)."""

    def __init__(self, max_concurrent_jobs: int = 2):
        self.processor = DocumentProcessor()
        self.max_concurrent_jobs = max_concurrent_jobs
        self.active_jobs = set()

    async def start_job(self, repository: EmbeddingJobRepository, job_id: int) -> bool:
        """Start an embedding job."""
        job = repository.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return False

        if job.status == "running":
            logger.warning(f"Job {job_id} is already running")
            return False

        if len(self.active_jobs) >= self.max_concurrent_jobs:
            logger.warning(f"Cannot start job {job_id}: max concurrent jobs limit reached")
            return False

        # Update job status
        repository.update(job_id, {"status": "running"})
        self.active_jobs.add(job_id)

        # Start job in background
        asyncio.create_task(self._run_job(repository, job_id))

        return True

    async def _run_job(self, repository: EmbeddingJobRepository, job_id: int) -> None:
        """Run an embedding job."""
        try:
            job = repository.get(job_id)
            if not job:
                logger.error(f"Job {job_id} not found when running")
                return

            logger.info(f"Starting embedding job {job_id} for website {job.website_id}")

            # Process the website
            start_time = time.time()
            result = self.processor.process_website(job.website_id)
            end_time = time.time()

            # Update job with results
            updates = {
                "status": "completed",
                "documents_found": result["documents_found"],
                "documents_processed": result["documents_processed"],
                "chunks_created": result["chunks_created"],
                "processing_time": end_time - start_time,
                "job_metadata": result
            }

            repository.update(job_id, updates)
            logger.info(f"Embedding job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Error in embedding job {job_id}: {str(e)}", exc_info=True)

            # Update job with error
            try:
                repository.update(job_id, {
                    "status": "failed",
                    "error": str(e)
                })
            except Exception as update_error:
                logger.error(f"Error updating job status: {str(update_error)}")

        finally:
            if job_id in self.active_jobs:
                self.active_jobs.remove(job_id)

    async def refresh_website(self, repository: EmbeddingJobRepository, website_id: int, force: bool = False) -> int:
        """Create and start a refresh job for a website."""
        # Create job
        job = repository.create({
            "website_id": website_id,
            "status": "pending",
            "is_refresh": True
        })

        # Start job
        await self.start_job(repository, job.id)

        return job.id

    def get_website_stats(self, website_id: int) -> Dict[str, Any]:
        """Get statistics about a website's embeddings."""
        return self.processor.get_website_stats(website_id)
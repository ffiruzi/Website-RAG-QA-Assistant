"""
Local simplified version of the crawler manager to avoid import issues.
"""
import asyncio
import logging
import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import os

import aiofiles

logger = logging.getLogger(__name__)

class CrawlerJob:
    """Represents a crawling job for a website."""

    def __init__(self, website_id: int, website_url: str, sitemap_url: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.website_id = website_id
        self.website_url = website_url
        self.sitemap_url = sitemap_url
        self.status = "pending"  # pending, running, completed, failed, stopped
        self.start_time = None
        self.end_time = None
        self.total_urls = 0
        self.processed_urls = 0
        self.successful_urls = 0
        self.failed_urls = 0
        self.errors = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        return {
            "id": self.id,
            "website_id": self.website_id,
            "website_url": self.website_url,
            "sitemap_url": self.sitemap_url,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_urls": self.total_urls,
            "processed_urls": self.processed_urls,
            "successful_urls": self.successful_urls,
            "failed_urls": self.failed_urls,
            "errors": self.errors,
            "progress": round((self.processed_urls / self.total_urls) * 100, 2) if self.total_urls > 0 else 0
        }


class LocalCrawlerManager:
    """A simplified local version of the CrawlerManager."""

    def __init__(self, storage_dir: str = "data/crawler"):
        self.jobs: Dict[str, CrawlerJob] = {}
        self.active_jobs: Set[str] = set()
        self.max_concurrent_jobs = 3
        self.storage_dir = storage_dir
        self.user_agent = "RAGCrawlerBot/1.0"

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "jobs"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "content"), exist_ok=True)

    def create_job(self, website_id: int, website_url: str, sitemap_url: Optional[str] = None) -> CrawlerJob:
        """Create a new crawling job."""
        job = CrawlerJob(website_id, website_url, sitemap_url)
        self.jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> Optional[CrawlerJob]:
        """Get a job by ID."""
        return self.jobs.get(job_id)

    def get_all_jobs(self) -> List[CrawlerJob]:
        """Get all jobs."""
        return list(self.jobs.values())

    def get_website_jobs(self, website_id: int) -> List[CrawlerJob]:
        """Get all jobs for a specific website."""
        return [job for job in self.jobs.values() if job.website_id == website_id]

    async def start_job(self, job_id: str) -> bool:
        """Start a job if it's not already running."""
        job = self.get_job(job_id)

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
        job.status = "running"
        job.start_time = datetime.now()
        self.active_jobs.add(job_id)

        # Start job in background (simulated)
        asyncio.create_task(self._simulate_job_running(job))

        return True

    async def _simulate_job_running(self, job: CrawlerJob) -> None:
        """Simulate a job running (placeholder for actual implementation)."""
        try:
            # Simulate crawling
            job.total_urls = 10  # Example value
            job.processed_urls = 0
            
            # Simulate processing URLs
            for i in range(job.total_urls):
                if job.status != "running":
                    break
                    
                await asyncio.sleep(1)  # Simulate processing time
                job.processed_urls += 1
                job.successful_urls += 1
                
            # Update job status
            if job.status == "running":
                job.status = "completed"
                job.end_time = datetime.now()
                
        except Exception as e:
            logger.error(f"Error in job {job.id}: {str(e)}")
            job.status = "failed"
            job.end_time = datetime.now()
            job.errors.append(str(e))
            
        finally:
            if job.id in self.active_jobs:
                self.active_jobs.remove(job.id)

    async def stop_job(self, job_id: str) -> bool:
        """Stop a running job."""
        job = self.get_job(job_id)

        if not job:
            logger.error(f"Job {job_id} not found")
            return False

        if job.status != "running":
            logger.warning(f"Job {job_id} is not running")
            return False

        # Update job status
        job.status = "stopped"
        job.end_time = datetime.now()
        self.active_jobs.remove(job_id)

        return True

    async def _save_content(self, website_id: int, content: Dict[str, Any]) -> None:
        """Save extracted content to disk and update database if available."""
        try:
            # Create folder for website if it doesn't exist
            website_dir = os.path.join(self.storage_dir, "content", str(website_id))
            os.makedirs(website_dir, exist_ok=True)

            # Generate a filename based on the URL
            url = content["url"]
            filename = f"{hash(url)}.json"
            file_path = os.path.join(website_dir, filename)

            # Save content to file
            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(content, indent=2))

            # Update database if possible
            try:
                # Import needed only when called
                from sqlalchemy.orm import Session
                from app.core.database import SessionLocal
                from app.repositories.page import PageRepository

                # Create session
                db = SessionLocal()
                try:
                    page_repo = PageRepository(db)

                    # Check if page exists
                    page = page_repo.get_by_url(url)

                    if page:
                        # Update existing page
                        page_repo.update(page.id, {
                            "title": content.get("title"),
                            "content": content.get("content"),
                            "last_crawled_at": datetime.now().isoformat()
                        })
                    else:
                        # Create new page
                        page_repo.create({
                            "url": url,
                            "title": content.get("title"),
                            "content": content.get("content"),
                            "website_id": website_id,
                            "last_crawled_at": datetime.now().isoformat(),
                            "is_indexed": False
                        })
                finally:
                    db.close()
            except Exception as db_error:
                # Log error but continue - this is just an enhancement
                logger.error(f"Error updating page in database: {str(db_error)}")

        except Exception as e:
            logger.error(f"Error saving content: {str(e)}")

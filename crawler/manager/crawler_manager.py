import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import os
import aiofiles
from sqlalchemy.orm import Session
import uuid
from pathlib import Path

from crawler.crawler.sitemap_crawler import EnhancedSitemapCrawler
from crawler.extractor.html_extractor import EnhancedHTMLContentExtractor

logger = logging.getLogger(__name__)


class CrawlerJob:
    """Represents a crawling job for a website."""

    def __init__(self, website_id: int, website_url: str, sitemap_url: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.website_id = website_id
        self.website_url = website_url
        self.sitemap_url = sitemap_url
        self.status = "pending"  # pending, running, completed, failed
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


class CrawlerManager:
    """Manages crawling jobs and their execution."""

    def __init__(self, storage_dir: str = "crawler_data"):
        self.jobs: Dict[str, CrawlerJob] = {}
        self.active_jobs: Set[str] = set()
        self.max_concurrent_jobs = 3
        self.storage_dir = storage_dir
        self.user_agent = "RAGCrawlerBot/1.0"
        self.default_crawl_delay = 1.0  # seconds

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "jobs"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "content"), exist_ok=True)

    def create_job(self, website_id: int, website_url: str, sitemap_url: Optional[str] = None) -> CrawlerJob:
        """Create a new crawling job."""
        job = CrawlerJob(website_id, website_url, sitemap_url)
        self.jobs[job.id] = job

        # Save job metadata
        self._save_job_metadata(job)

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

        # Save updated job metadata
        self._save_job_metadata(job)

        # Start job in background
        asyncio.create_task(self._run_job(job))

        return True

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

        # Save updated job metadata
        self._save_job_metadata(job)

        return True

    async def _run_job(self, job: CrawlerJob) -> None:
        """Run a crawling job."""
        try:
            logger.info(f"Starting job {job.id} for website {job.website_url}")

            # Create crawler and extractor
            crawler = EnhancedSitemapCrawler(job.website_url, self.user_agent)
            extractor = EnhancedHTMLContentExtractor(self.user_agent)

            # Discover URLs
            urls_data = await crawler.crawl()
            urls = [url_data["url"] for url_data in urls_data]

            job.total_urls = len(urls)
            self._save_job_metadata(job)

            logger.info(f"Job {job.id}: Discovered {len(urls)} URLs")

            # Process URLs in batches to control memory usage
            batch_size = 10
            for i in range(0, len(urls), batch_size):
                if job.status != "running":
                    logger.info(f"Job {job.id} was stopped")
                    break

                batch = urls[i:i + batch_size]
                content_results = await extractor.extract_from_urls(batch, delay=self.default_crawl_delay)

                for result in content_results:
                    if job.status != "running":
                        break

                    url = result.get("url")

                    if "error" in result:
                        logger.warning(f"Failed to extract content from {url}: {result['error']}")
                        job.failed_urls += 1
                        job.errors.append(f"Failed to extract content from {url}: {result['error']}")
                    else:
                        # Save content to file
                        await self._save_content(job.website_id, result)
                        job.successful_urls += 1

                    job.processed_urls += 1
                    self._save_job_metadata(job)

                logger.info(f"Job {job.id}: Processed {job.processed_urls}/{job.total_urls} URLs")

            # Update job status
            if job.status == "running":
                job.status = "completed"
                job.end_time = datetime.now()
                logger.info(f"Job {job.id} completed successfully")
            else:
                logger.info(f"Job {job.id} was stopped before completion")

        except Exception as e:
            logger.error(f"Error in job {job.id}: {str(e)}", exc_info=True)
            job.status = "failed"
            job.end_time = datetime.now()
            job.errors.append(str(e))

        finally:
            if job.id in self.active_jobs:
                self.active_jobs.remove(job.id)

            self._save_job_metadata(job)

    def _save_job_metadata(self, job: CrawlerJob) -> None:
        """Save job metadata to disk."""
        try:
            job_path = os.path.join(self.storage_dir, "jobs", f"{job.id}.json")
            with open(job_path, "w") as f:
                json.dump(job.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving job metadata: {str(e)}")

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

    def load_jobs(self) -> None:
        """Load saved jobs from disk."""
        try:
            jobs_dir = os.path.join(self.storage_dir, "jobs")
            if not os.path.exists(jobs_dir):
                return

            for filename in os.listdir(jobs_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(jobs_dir, filename), "r") as f:
                            job_data = json.load(f)
                            job = CrawlerJob(
                                website_id=job_data["website_id"],
                                website_url=job_data["website_url"],
                                sitemap_url=job_data["sitemap_url"]
                            )
                            job.id = job_data["id"]
                            job.status = job_data["status"]
                            job.start_time = datetime.fromisoformat(job_data["start_time"]) if job_data[
                                "start_time"] else None
                            job.end_time = datetime.fromisoformat(job_data["end_time"]) if job_data[
                                "end_time"] else None
                            job.total_urls = job_data["total_urls"]
                            job.processed_urls = job_data["processed_urls"]
                            job.successful_urls = job_data["successful_urls"]
                            job.failed_urls = job_data["failed_urls"]
                            job.errors = job_data["errors"]

                            self.jobs[job.id] = job
                    except Exception as e:
                        logger.error(f"Error loading job from {filename}: {str(e)}")

        except Exception as e:
            logger.error(f"Error loading jobs: {str(e)}")

    async def resume_job(self, job_id: str) -> bool:
        """Resume a failed or stopped job."""
        job = self.get_job(job_id)

        if not job:
            logger.error(f"Job {job_id} not found")
            return False

        if job.status not in ["failed", "stopped"]:
            logger.warning(f"Cannot resume job {job_id} with status {job.status}")
            return False

        if len(self.active_jobs) >= self.max_concurrent_jobs:
            logger.warning(f"Cannot resume job {job_id}: max concurrent jobs limit reached")
            return False

        # Update job status
        job.status = "running"
        self.active_jobs.add(job_id)

        # Save updated job metadata
        self._save_job_metadata(job)

        # Start job in background
        asyncio.create_task(self._resume_job(job))

        return True

    async def _resume_job(self, job: CrawlerJob) -> None:
        """Resume a job from where it left off."""
        try:
            logger.info(f"Resuming job {job.id} for website {job.website_url}")

            # Create crawler and extractor
            crawler = EnhancedSitemapCrawler(job.website_url, self.user_agent)
            extractor = EnhancedHTMLContentExtractor(self.user_agent)

            # If we already have URL data, no need to re-crawl
            if job.total_urls > 0:
                # Find already processed URLs
                website_dir = os.path.join(self.storage_dir, "content", str(job.website_id))
                processed_urls = set()

                if os.path.exists(website_dir):
                    for filename in os.listdir(website_dir):
                        if filename.endswith(".json"):
                            try:
                                with open(os.path.join(website_dir, filename), "r") as f:
                                    content = json.load(f)
                                    processed_urls.add(content["url"])
                            except Exception as e:
                                logger.error(f"Error loading content: {str(e)}")

                # Re-crawl to get URLs
                urls_data = await crawler.crawl()
                urls = [url_data["url"] for url_data in urls_data if url_data["url"] not in processed_urls]

                # Update job status
                remaining_urls = len(urls)
                job.total_urls = job.processed_urls + remaining_urls
                self._save_job_metadata(job)

                logger.info(f"Job {job.id}: Found {remaining_urls} new URLs to process")

                # Process remaining URLs
                batch_size = 10
                for i in range(0, len(urls), batch_size):
                    if job.status != "running":
                        logger.info(f"Job {job.id} was stopped")
                        break

                    batch = urls[i:i + batch_size]
                    content_results = await extractor.extract_from_urls(batch, delay=self.default_crawl_delay)

                    for result in content_results:
                        if job.status != "running":
                            break

                        url = result.get("url")

                        if "error" in result:
                            logger.warning(f"Failed to extract content from {url}: {result['error']}")
                            job.failed_urls += 1
                            job.errors.append(f"Failed to extract content from {url}: {result['error']}")
                        else:
                            # Save content to file
                            await self._save_content(job.website_id, result)
                            job.successful_urls += 1

                        job.processed_urls += 1
                        self._save_job_metadata(job)

                    logger.info(f"Job {job.id}: Processed {job.processed_urls}/{job.total_urls} URLs")

            else:
                # This should rarely happen, but handle it just in case
                await self._run_job(job)
                return

            # Update job status
            if job.status == "running":
                job.status = "completed"
                job.end_time = datetime.now()
                logger.info(f"Job {job.id} completed successfully")
            else:
                logger.info(f"Job {job.id} was stopped before completion")

        except Exception as e:
            logger.error(f"Error in job {job.id}: {str(e)}", exc_info=True)
            job.status = "failed"
            job.end_time = datetime.now()
            job.errors.append(str(e))

        finally:
            if job.id in self.active_jobs:
                self.active_jobs.remove(job.id)

            self._save_job_metadata(job)




# Example usage
async def example_usage():
    manager = CrawlerManager()

    # Load existing jobs
    manager.load_jobs()

    # Create a new job
    job = manager.create_job(1, "https://example.com")

    # Start the job
    await manager.start_job(job.id)

    # Wait for the job to finish
    while job.status == "running":
        print(f"Job progress: {job.processed_urls}/{job.total_urls} URLs processed")
        await asyncio.sleep(5)

    print(f"Job completed with status: {job.status}")
    print(f"Processed {job.successful_urls} URLs successfully")
    print(f"Failed to process {job.failed_urls} URLs")

    if job.errors:
        print(f"Job errors: {job.errors}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
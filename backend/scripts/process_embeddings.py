#!/usr/bin/env python
import os
import sys
import asyncio
import argparse
import logging
from typing import List, Optional

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.repositories.website import WebsiteRepository
from app.repositories.embedding_job import EmbeddingJobRepository
from app.services.embedding_manager import EmbeddingManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def process_website(website_id: int, force: bool = False) -> None:
    """Process embeddings for a single website."""
    db = SessionLocal()
    try:
        website_repo = WebsiteRepository(db)
        job_repo = EmbeddingJobRepository(db)

        website = website_repo.get(website_id)
        if not website:
            logger.error(f"Website with ID {website_id} not found")
            return

        logger.info(f"Processing website: {website.name} (ID: {website.id})")

        manager = EmbeddingManager()
        job_id = await manager.refresh_website(job_repo, website.id, force)

        logger.info(f"Started embedding job {job_id} for website {website.id}")

        # Wait for job to complete
        while True:
            job = job_repo.get(job_id)
            if job.status != "running":
                break
            logger.info(
                f"Job {job_id} is running... ({job.documents_processed}/{job.documents_found} documents processed)")
            await asyncio.sleep(5)

        if job.status == "completed":
            logger.info(
                f"Job {job_id} completed successfully. Processed {job.documents_processed} documents, created {job.chunks_created} chunks.")
        else:
            logger.error(f"Job {job_id} failed: {job.error}")

    finally:
        db.close()


async def process_all_websites(force: bool = False) -> None:
    """Process embeddings for all active websites."""
    db = SessionLocal()
    try:
        website_repo = WebsiteRepository(db)

        websites = website_repo.get_active_websites()
        logger.info(f"Found {len(websites)} active websites")

        for website in websites:
            await process_website(website.id, force)

    finally:
        db.close()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Process website embeddings")
    parser.add_argument("--website-id", type=int,
                        help="ID of the website to process (omit to process all active websites)")
    parser.add_argument("--force", action="store_true", help="Force reprocessing of all content")

    args = parser.parse_args()

    if args.website_id:
        await process_website(args.website_id, args.force)
    else:
        await process_all_websites(args.force)


if __name__ == "__main__":
    asyncio.run(main())
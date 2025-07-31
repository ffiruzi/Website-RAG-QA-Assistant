from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, Query, status
from sqlalchemy.orm import Session
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from app.core.database import get_db
from app.repositories.website import WebsiteRepository
from app.api.dependencies import get_website_repository
from crawler.manager.crawler_manager import CrawlerManager

router = APIRouter()

# Create a singleton instance of CrawlerManager
crawler_manager = CrawlerManager(storage_dir="data/crawler")

# On application startup, load existing jobs
crawler_manager.load_jobs()


@router.post("/crawl/{website_id}", status_code=status.HTTP_202_ACCEPTED)
async def start_crawl(
        website_id: int = Path(..., description="The ID of the website to crawl"),
        background_tasks: BackgroundTasks = None,
        repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Start a crawling job for a website.
    """
    # Check if website exists
    website = repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # Create crawl job
    job = crawler_manager.create_job(
        website_id=website.id,
        website_url=website.url,
        sitemap_url=website.sitemap_url
    )

    # Start job in background
    started = await crawler_manager.start_job(job.id)

    if not started:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to start crawling job, maximum concurrent jobs reached or job is already running"
        )

    return {"job_id": job.id, "status": job.status}


@router.get("/jobs", response_model=List[Dict[str, Any]])
async def get_all_jobs():
    """
    Get all crawling jobs.
    """
    jobs = crawler_manager.get_all_jobs()
    return [job.to_dict() for job in jobs]


@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
async def get_job(
        job_id: str = Path(..., description="The ID of the job to get")
):
    """
    Get a crawling job by ID.
    """
    job = crawler_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )

    return job.to_dict()


@router.get("/websites/{website_id}/jobs", response_model=List[Dict[str, Any]])
async def get_website_jobs(
        website_id: int = Path(..., description="The ID of the website to get jobs for")
):
    """
    Get all crawling jobs for a website.
    """
    jobs = crawler_manager.get_website_jobs(website_id)
    return [job.to_dict() for job in jobs]


@router.post("/jobs/{job_id}/stop", status_code=status.HTTP_202_ACCEPTED)
async def stop_job(
        job_id: str = Path(..., description="The ID of the job to stop")
):
    """
    Stop a running crawling job.
    """
    job = crawler_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )

    if job.status != "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is not running (current status: {job.status})"
        )

    stopped = await crawler_manager.stop_job(job_id)
    if not stopped:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop crawling job"
        )

    return {"job_id": job_id, "status": "stopped"}


@router.post("/jobs/{job_id}/resume", status_code=status.HTTP_202_ACCEPTED)
async def resume_job(
        job_id: str = Path(..., description="The ID of the job to resume")
):
    """
    Resume a failed or stopped crawling job.
    """
    job = crawler_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )

    if job.status not in ["failed", "stopped"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job cannot be resumed (current status: {job.status})"
        )

    resumed = await crawler_manager.resume_job(job_id)
    if not resumed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume crawling job"
        )

    return {"job_id": job_id, "status": "running"}
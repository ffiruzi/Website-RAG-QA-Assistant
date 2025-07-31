from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, Query, status
from sqlalchemy.orm import Session
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from app.core.database import get_db
from app.schemas.embedding_job import EmbeddingJobCreate, EmbeddingJobUpdate, EmbeddingJobResponse
from app.repositories.embedding_job import EmbeddingJobRepository
from app.repositories.website import WebsiteRepository
from app.services.embedding_manager import EmbeddingManager

router = APIRouter()

# Create a singleton instance of EmbeddingManager
embedding_manager = EmbeddingManager()

def get_embedding_job_repository(db: Session = Depends(get_db)) -> EmbeddingJobRepository:
    return EmbeddingJobRepository(db)

def get_website_repository(db: Session = Depends(get_db)) -> WebsiteRepository:
    return WebsiteRepository(db)

@router.post("/{website_id}/process", response_model=EmbeddingJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_embedding_process(
        website_id: int = Path(..., description="The ID of the website to process"),
        force_refresh: bool = Query(False, description="Whether to force reprocessing of all URLs"),
        repository: EmbeddingJobRepository = Depends(get_embedding_job_repository),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Start an embedding process for a website.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # Create embedding job
    job = repository.create({
        "website_id": website_id,
        "status": "pending",
        "is_refresh": force_refresh
    })

    # Start job
    started = await embedding_manager.start_job(repository, job.id)

    if not started:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to start embedding job, maximum concurrent jobs reached or job is already running"
        )

    return job

@router.get("/{website_id}/jobs", response_model=List[EmbeddingJobResponse])
def get_website_embedding_jobs(
        website_id: int = Path(..., description="The ID of the website to get jobs for"),
        repository: EmbeddingJobRepository = Depends(get_embedding_job_repository),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Get all embedding jobs for a website.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    return repository.get_by_website_id(website_id)

@router.get("/{website_id}/stats", response_model=Dict[str, Any])
def get_website_embedding_stats(
        website_id: int = Path(..., description="The ID of the website to get stats for"),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Get embedding statistics for a website.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    return embedding_manager.get_website_stats(website_id)

@router.get("/jobs/{job_id}", response_model=EmbeddingJobResponse)
def get_embedding_job(
        job_id: int = Path(..., description="The ID of the job to get"),
        repository: EmbeddingJobRepository = Depends(get_embedding_job_repository)
):
    """
    Get an embedding job by ID.
    """
    job = repository.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Embedding job with ID {job_id} not found"
        )

    return job

@router.get("/jobs", response_model=List[EmbeddingJobResponse])
def get_all_embedding_jobs(
        status: Optional[str] = Query(None, description="Filter jobs by status"),
        repository: EmbeddingJobRepository = Depends(get_embedding_job_repository)
):
    """
    Get all embedding jobs, optionally filtered by status.
    """
    if status:
        return repository.get_jobs_by_status(status)
    else:
        return repository.get_all()
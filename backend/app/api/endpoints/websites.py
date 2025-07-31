
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path as FastAPIPath
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.website import Website
from app.repositories.website import WebsiteRepository
from app.repositories.page import PageRepository
from app.repositories.embedding_job import EmbeddingJobRepository
from app.schemas.website import WebsiteCreate, WebsiteUpdate, WebsiteResponse
from app.services.document_processor import DocumentProcessor
from app.api.dependencies import (
    get_website_repository,
    get_pagination,
    PaginationParams,
    PaginatedResponse,
    get_current_active_user,
    get_current_active_superuser
)
from app.models.user import User
from app.core.errors import NotFoundError, BadRequestError


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[WebsiteResponse])
def read_websites(
        name: Optional[str] = Query(None, description="Filter by name"),
        url: Optional[str] = Query(None, description="Filter by URL"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        pagination: PaginationParams = Depends(get_pagination),
        repository: WebsiteRepository = Depends(get_website_repository),
        current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all websites with pagination and filtering.
    """
    filters = {}
    if name:
        filters["name"] = name
    if url:
        filters["url"] = url
    if is_active is not None:
        filters["is_active"] = is_active

    # Get total count
    total = repository.count_filtered(**filters)

    # Get paginated results
    websites = repository.get_filtered(
        skip=pagination.offset,
        limit=pagination.page_size,
        order_by=pagination.sort_by or "id",
        sort_order=pagination.sort_order,
        **filters
    )

    # Calculate total pages
    pages = (total + pagination.page_size - 1) // pagination.page_size

    return {
        "items": websites,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "pages": pages
    }


@router.get("/{website_id}/status", response_model=Dict[str, Any])
def get_website_status(
        website_id: int = FastAPIPath(..., description="The ID of the website"),
        repository: WebsiteRepository = Depends(get_website_repository),
        db: Session = Depends(get_db)
):
    """
    Get the status of a website's crawling and embedding processes.
    """
    # Check if website exists
    website = repository.get(website_id)
    if website is None:
        raise NotFoundError(f"Website with ID {website_id} not found")

    # Import repositories needed for status checking
    from app.repositories.embedding_job import EmbeddingJobRepository
    from app.repositories.page import PageRepository
    from app.services.document_processor import DocumentProcessor

    # Initialize repositories
    embedding_job_repo = EmbeddingJobRepository(db)
    page_repo = PageRepository(db)
    document_processor = DocumentProcessor()

    # Get the latest crawling job
    # This is a placeholder - in a real implementation, you would get this from the crawler service
    # For now, we'll check if the website has any pages
    pages = page_repo.get_by_website_id(website_id)
    page_count = len(pages)

    # Get the latest embedding job
    latest_embedding_job = embedding_job_repo.get_latest_by_website_id(website_id)

    # Get embedding stats
    embedding_stats = document_processor.get_website_stats(website_id)


    # Determine crawling status
    if page_count > 0:
        crawling_status = "Completed"
        # Check if there are any pages with recent crawl date
        pages_with_crawl_date = [p for p in pages if p.last_crawled_at]
        if pages_with_crawl_date:
            last_crawled_page = max(pages_with_crawl_date, key=lambda p: p.last_crawled_at)
            last_crawled_at = last_crawled_page.last_crawled_at
        else:
            last_crawled_at = None
    else:
        # Check if there's an active crawling job (this would require integration with the crawler service)
        # For now, we'll assume there's no active job if there are no pages
        crawling_status = "Not crawled"
        last_crawled_at = None


    # Determine embedding status
    if latest_embedding_job:
        if latest_embedding_job.status == "running":
            embedding_status = "Running"
        elif latest_embedding_job.status == "completed":
            embedding_status = "Completed"
        elif latest_embedding_job.status == "failed":
            embedding_status = "Failed"
        else:
            embedding_status = "Pending"
        last_embedded_at = latest_embedding_job.updated_at.isoformat() if latest_embedding_job.updated_at else None
    else:
        embedding_status = "Not generated"
        last_embedded_at = None

    # Get document and embedding counts
    document_count = page_count
    embedding_count = embedding_stats.get("embedding_count", 0) if embedding_stats.get("status") == "success" else 0

    return {
        "crawling_status": crawling_status,
        "embedding_status": embedding_status,
        "document_count": document_count,
        "embedding_count": embedding_count,
        "last_crawled_at": last_crawled_at,
        "last_embedded_at": last_embedded_at
    }



@router.post("/", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
def create_website(
        website: WebsiteCreate,
        repository: WebsiteRepository = Depends(get_website_repository),
        current_user: User = Depends(get_current_active_superuser)
):
    """
    Create a new website.
    """
    # Check if website with this URL already exists
    existing_website = repository.get_by_url(website.url)
    if existing_website:
        raise BadRequestError(f"Website with URL '{website.url}' already exists")

    return repository.create(website)


@router.get("/{website_id}", response_model=WebsiteResponse)
def read_website(
        website_id: int,
        repository: WebsiteRepository = Depends(get_website_repository),
        current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a website by ID.
    """
    website = repository.get(website_id)
    if website is None:
        raise NotFoundError(f"Website with ID {website_id} not found")
    return website


@router.put("/{website_id}", response_model=WebsiteResponse)
def update_website(
        website_id: int,
        website_update: WebsiteUpdate,
        repository: WebsiteRepository = Depends(get_website_repository),
        current_user: User = Depends(get_current_active_superuser)
):
    """
    Update a website.
    """
    # Check if website exists
    existing_website = repository.get(website_id)
    if existing_website is None:
        raise NotFoundError(f"Website with ID {website_id} not found")

    # If URL is being updated, check if it already exists
    if website_update.url is not None and website_update.url != existing_website.url:
        website_with_url = repository.get_by_url(website_update.url)
        if website_with_url is not None:
            raise BadRequestError(f"Website with URL '{website_update.url}' already exists")

    updated_website = repository.update(website_id, website_update)
    if updated_website is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the website"
        )

    return updated_website


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_website(
        website_id: int,
        repository: WebsiteRepository = Depends(get_website_repository),
        current_user: User = Depends(get_current_active_superuser)
):
    """
    Delete a website.
    """
    # Check if website exists
    existing_website = repository.get(website_id)
    if existing_website is None:
        raise NotFoundError(f"Website with ID {website_id} not found")

    if not repository.delete(website_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the website"
        )
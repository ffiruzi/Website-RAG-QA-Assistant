from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_active_superuser
from app.repositories.webhook import WebhookRepository
from app.repositories.webhook_log import WebhookLogRepository
from app.repositories.website import WebsiteRepository
from app.schemas.webhook import WebhookCreate, WebhookUpdate, WebhookResponse, WebhookLogResponse
from app.models.user import User
from app.services.webhook_service import WebhookService

router = APIRouter()


def get_webhook_repository(db: Session = Depends(get_db)) -> WebhookRepository:
    return WebhookRepository(db)


def get_webhook_log_repository(db: Session = Depends(get_db)) -> WebhookLogRepository:
    return WebhookLogRepository(db)


def get_website_repository(db: Session = Depends(get_db)) -> WebsiteRepository:
    return WebsiteRepository(db)


def get_webhook_service(
        webhook_repo: WebhookRepository = Depends(get_webhook_repository),
        log_repo: WebhookLogRepository = Depends(get_webhook_log_repository)
) -> WebhookService:
    return WebhookService(webhook_repo, log_repo)


@router.get("/{website_id}", response_model=List[WebhookResponse])
def get_website_webhooks(
        website_id: int = Path(..., description="The ID of the website"),
        current_user: User = Depends(get_current_active_superuser),
        repository: WebhookRepository = Depends(get_webhook_repository),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Get all webhooks for a website.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    return repository.get_by_website_id(website_id)


@router.post("/{website_id}", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
        website_id: int = Path(..., description="The ID of the website"),
        webhook: WebhookCreate = None,
        current_user: User = Depends(get_current_active_superuser),
        repository: WebhookRepository = Depends(get_webhook_repository),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Create a new webhook for a website.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # Ensure website_id in path matches webhook.website_id
    if webhook.website_id != website_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website ID in path must match webhook website_id"
        )

    return repository.create(webhook)


@router.get("/{website_id}/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
        website_id: int = Path(..., description="The ID of the website"),
        webhook_id: int = Path(..., description="The ID of the webhook"),
        current_user: User = Depends(get_current_active_superuser),
        repository: WebhookRepository = Depends(get_webhook_repository)
):
    """
    Get a webhook by ID.
    """
    webhook = repository.get(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found"
        )

    # Check if webhook belongs to the specified website
    if webhook.website_id != website_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found for website {website_id}"
        )

    return webhook


@router.put("/{website_id}/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
        website_id: int = Path(..., description="The ID of the website"),
        webhook_id: int = Path(..., description="The ID of the webhook"),
        webhook: WebhookUpdate = None,
        current_user: User = Depends(get_current_active_superuser),
        repository: WebhookRepository = Depends(get_webhook_repository)
):
    """
    Update a webhook.
    """
    db_webhook = repository.get(webhook_id)
    if not db_webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found"
        )

    # Check if webhook belongs to the specified website
    if db_webhook.website_id != website_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found for website {website_id}"
        )

    return repository.update(webhook_id, webhook)


@router.delete("/{website_id}/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
        website_id: int = Path(..., description="The ID of the website"),
        webhook_id: int = Path(..., description="The ID of the webhook"),
        current_user: User = Depends(get_current_active_superuser),
        repository: WebhookRepository = Depends(get_webhook_repository)
):
    """
    Delete a webhook.
    """
    webhook = repository.get(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found"
        )

    # Check if webhook belongs to the specified website
    if webhook.website_id != website_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found for website {website_id}"
        )

    repository.delete(webhook_id)


@router.get("/{website_id}/{webhook_id}/logs", response_model=List[WebhookLogResponse])
def get_webhook_logs(
        website_id: int = Path(..., description="The ID of the website"),
        webhook_id: int = Path(..., description="The ID of the webhook"),
        limit: int = Query(100, description="Number of logs to return"),
        current_user: User = Depends(get_current_active_superuser),
        webhook_repository: WebhookRepository = Depends(get_webhook_repository),
        log_repository: WebhookLogRepository = Depends(get_webhook_log_repository)
):
    """
    Get logs for a webhook.
    """
    webhook = webhook_repository.get(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found"
        )

    # Check if webhook belongs to the specified website
    if webhook.website_id != website_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found for website {website_id}"
        )

    return log_repository.get_by_webhook_id(webhook_id, limit)


@router.post("/{website_id}/{webhook_id}/test", response_model=Dict[str, Any])
async def test_webhook(
        website_id: int = Path(..., description="The ID of the website"),
        webhook_id: int = Path(..., description="The ID of the webhook"),
        current_user: User = Depends(get_current_active_superuser),
        webhook_repository: WebhookRepository = Depends(get_webhook_repository),
        webhook_service: WebhookService = Depends(get_webhook_service),
        background_tasks: BackgroundTasks = None
):
    """
    Test a webhook by sending a test payload.
    """
    webhook = webhook_repository.get(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found"
        )

    # Check if webhook belongs to the specified website
    if webhook.website_id != website_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with ID {webhook_id} not found for website {website_id}"
        )

    # Test payload
    test_payload = {
        "type": "test",
        "message": "This is a test webhook"
    }

    # Trigger the webhook in the background to avoid blocking the API
    background_tasks.add_task(
        webhook_service.trigger_webhook,
        webhook,
        "test",
        test_payload
    )

    return {"success": True, "message": "Test webhook triggered"}
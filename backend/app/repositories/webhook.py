from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookUpdate
from app.repositories.base import BaseRepository


class WebhookRepository(BaseRepository[Webhook, WebhookCreate, WebhookUpdate]):
    def __init__(self, db: Session):
        super().__init__(Webhook, db)

    def get_by_website_id(self, website_id: int) -> List[Webhook]:
        """Get all webhooks for a website."""
        return self.db.query(Webhook).filter(Webhook.website_id == website_id).all()

    def get_active_by_website_id(self, website_id: int) -> List[Webhook]:
        """Get all active webhooks for a website."""
        return self.db.query(Webhook).filter(
            Webhook.website_id == website_id,
            Webhook.is_active == True
        ).all()
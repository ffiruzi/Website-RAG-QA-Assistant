from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.webhook_log import WebhookLog
from app.schemas.webhook import WebhookLogCreate
from app.repositories.base import BaseRepository


class WebhookLogRepository(BaseRepository[WebhookLog, WebhookLogCreate, None]):
    def __init__(self, db: Session):
        super().__init__(WebhookLog, db)

    def get_by_webhook_id(self, webhook_id: int, limit: int = 100) -> List[WebhookLog]:
        """Get logs for a webhook."""
        return self.db.query(WebhookLog)\
            .filter(WebhookLog.webhook_id == webhook_id)\
            .order_by(WebhookLog.created_at.desc())\
            .limit(limit)\
            .all()
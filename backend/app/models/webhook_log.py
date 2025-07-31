from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedBase


class WebhookLog(TimeStampedBase):
    __tablename__ = "webhook_logs"

    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    event = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    response_code = Column(Integer, nullable=True)
    response_body = Column(String, nullable=True)
    success = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)

    # Relationships
    webhook = relationship("Webhook")

    def __repr__(self):
        return f"<WebhookLog {self.id} for webhook {self.webhook_id} ({self.event})>"
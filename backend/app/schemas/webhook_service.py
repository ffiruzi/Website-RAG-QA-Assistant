import logging
import json
import hmac
import hashlib
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.repositories.webhook import WebhookRepository
from app.repositories.webhook_log import WebhookLogRepository
from app.models.webhook import Webhook

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing and triggering webhooks."""

    def __init__(self, webhook_repository: WebhookRepository, log_repository: WebhookLogRepository):
        self.webhook_repository = webhook_repository
        self.log_repository = log_repository

    def get_website_webhooks(self, website_id: int, event: str) -> List[Webhook]:
        """Get all active webhooks for a website that should be triggered for an event."""
        all_webhooks = self.webhook_repository.get_active_by_website_id(website_id)
        return [wh for wh in all_webhooks if event in wh.events]

    def create_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Create a signature for a webhook payload."""
        payload_str = json.dumps(payload)
        return hmac.new(
            secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def trigger_webhook(self, webhook: Webhook, event: str, payload: Dict[str, Any]) -> bool:
        """Trigger a webhook by sending the payload to the URL."""
        # Add event and timestamp to payload
        webhook_payload = {
            **payload,
            "event": event,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Create headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Website-RAG-QA-Webhook/1.0",
            "X-Event-Name": event
        }

        # Add signature if secret is provided
        if webhook.secret:
            signature = self.create_signature(webhook_payload, webhook.secret)
            headers["X-Webhook-Signature"] = signature

        success = False
        response_code = None
        response_body = None
        error_message = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(str(webhook.url),
                                        json=webhook_payload,
                                        headers=headers,
                                        timeout=10) as response:
                    response_code = response.status
                    response_body = await response.text()
                    success = 200 <= response.status < 300

        except Exception as e:
            error_message = str(e)
            logger.error(f"Error triggering webhook {webhook.id}: {error_message}")

        # Log the webhook call
        self.log_repository.create({
            "webhook_id": webhook.id,
            "event": event,
            "payload": webhook_payload,
            "response_code": response_code,
            "response_body": response_body,
            "success": success,
            "error_message": error_message
        })

        return success

    async def trigger_event(self, website_id: int, event: str, payload: Dict[str, Any]) -> int:
        """Trigger all webhooks for a website and event."""
        webhooks = self.get_website_webhooks(website_id, event)

        if not webhooks:
            return 0

        # Trigger all webhooks in parallel
        tasks = [self.trigger_webhook(webhook, event, payload) for webhook in webhooks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful triggers
        successful = sum(1 for r in results if r is True)

        return successful
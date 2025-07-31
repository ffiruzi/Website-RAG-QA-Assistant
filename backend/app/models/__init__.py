"""
Models module - Import order is important for relationships.
"""

# Import base first
from .base import TimeStampedBase

# Import models in dependency order
from .website import Website
from .page import Page
from .chunk import Chunk
from .conversation import Conversation
from .message import Message
from .embedding_job import EmbeddingJob
from .user import User
from .webhook import Webhook
from .webhook_log import WebhookLog

# Make sure all models are available
__all__ = [
    "TimeStampedBase",
    "Website", 
    "Page",
    "Chunk",
    "Conversation",
    "Message", 
    "EmbeddingJob",
    "User",
    "Webhook",
    "WebhookLog"
]
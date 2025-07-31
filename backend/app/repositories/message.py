from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message, MessageCreate, MessageUpdate]):
    def __init__(self, db: Session):
        super().__init__(Message, db)

    def get_by_conversation_id(self, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation."""
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
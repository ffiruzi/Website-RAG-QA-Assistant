from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation, ConversationCreate, ConversationUpdate]):
    def __init__(self, db: Session):
        super().__init__(Conversation, db)

    def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Get a conversation by session ID."""
        return self.db.query(Conversation).filter(Conversation.session_id == session_id).first()

    def get_by_website_id(self, website_id: int) -> List[Conversation]:
        """Get all conversations for a website."""
        return self.db.query(Conversation).filter(Conversation.website_id == website_id).all()
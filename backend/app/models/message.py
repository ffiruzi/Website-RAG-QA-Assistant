from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedBase


class Message(TimeStampedBase):
    __tablename__ = "messages"

    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, default=True)
    sources = Column(Text, nullable=True)  # JSON string of source URLs

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id} from conversation {self.conversation_id}>"
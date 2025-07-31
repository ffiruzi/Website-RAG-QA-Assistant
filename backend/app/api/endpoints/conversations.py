from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.conversation import ConversationResponse
from app.schemas.message import MessageResponse

router = APIRouter()


def get_conversation_repository(db: Session = Depends(get_db)) -> ConversationRepository:
    return ConversationRepository(db)


def get_message_repository(db: Session = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)


@router.get("/", response_model=List[ConversationResponse])
def get_all_conversations(
        repository: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Get all conversations.
    """
    return repository.get_all()


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
        conversation_id: int = Path(..., description="The ID of the conversation to get"),
        repository: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Get a specific conversation by ID.
    """
    conversation = repository.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return conversation


@router.get("/website/{website_id}", response_model=List[ConversationResponse])
def get_website_conversations(
        website_id: int = Path(..., description="The ID of the website to get conversations for"),
        repository: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Get all conversations for a website.
    """
    return repository.get_by_website_id(website_id)


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
        conversation_id: int = Path(..., description="The ID of the conversation to get messages for"),
        repository: ConversationRepository = Depends(get_conversation_repository),
        message_repository: MessageRepository = Depends(get_message_repository)
):
    """
    Get all messages for a conversation.
    """
    conversation = repository.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )

    return message_repository.get_by_conversation_id(conversation_id)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
        conversation_id: int = Path(..., description="The ID of the conversation to delete"),
        repository: ConversationRepository = Depends(get_conversation_repository)
):
    """
    Delete a conversation and all its messages.
    """
    conversation = repository.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )

    success = repository.delete(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )
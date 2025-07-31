import json
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, BackgroundTasks, Header
from sqlalchemy.orm import Session
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from app.core.database import get_db
from app.repositories.website import WebsiteRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.services.search_service import SearchService
from app.services.rag_service import RAGService
from app.schemas.message import MessageCreate

router = APIRouter()

# Create singleton instances of services
search_service = SearchService()
rag_service = RAGService()


def get_website_repository(db: Session = Depends(get_db)) -> WebsiteRepository:
    return WebsiteRepository(db)


def get_conversation_repository(db: Session = Depends(get_db)) -> ConversationRepository:
    return ConversationRepository(db)


def get_message_repository(db: Session = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)


@router.get("/{website_id}/search", response_model=List[Dict[str, Any]])
def search_website(
        website_id: int = Path(..., description="The ID of the website to search"),
        query: str = Query(..., description="Search query"),
        limit: int = Query(5, description="Number of results to return"),
        offset: int = Query(0, description="Number of results to skip"),
        min_score: float = Query(0.0, description="Minimum similarity score threshold"),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Search for documents on a website.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    return search_service.search(
        website_id=website_id,
        query=query,
        top_k=limit,
        offset=offset,
        min_score=min_score
    )


@router.post("/{website_id}/ask", response_model=Dict[str, Any])
async def ask_question(
        website_id: int = Path(..., description="The ID of the website to query"),
        query: str = Query(..., description="User query"),
        session_id: str = Query("default", description="Session ID for conversation history"),
        use_history: bool = Query(True, description="Whether to use conversation history"),
        save_conversation: bool = Query(True, description="Whether to save the conversation"),
        temperature: float = Query(0.2, description="Temperature for answer generation"),
        stream: bool = Query(False, description="Whether to stream the response"),
        user_info: Optional[str] = Query(None, description="Optional user information in JSON format"),
        website_repository: WebsiteRepository = Depends(get_website_repository),
        conversation_repository: ConversationRepository = Depends(get_conversation_repository),
        message_repository: MessageRepository = Depends(get_message_repository),
        background_tasks: BackgroundTasks = None,
        user_agent: Optional[str] = Header(None)
):
    """
    Ask a question and get an answer from a website using RAG.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # Parse user info if provided
    user_data = {}
    if user_info:
        try:
            user_data = json.loads(user_info)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_info JSON format"
            )

    # Use website-specific prompt template if available
    prompt_template_id = website.prompt_template_id

    # Use RAG service to get answer
    result = rag_service.answer_query(
        website_id=website_id,
        query=query,
        session_id=session_id,
        use_chat_history=use_history
    )

    # Save conversation in background if requested
    if save_conversation:
        background_tasks.add_task(
            save_conversation_and_messages,
            conversation_repository,
            message_repository,
            website_id,
            session_id,
            query,
            result,
            user_data
        )

    return result


@router.post("/{website_id}/reset", response_model=Dict[str, bool])
def reset_conversation(
        website_id: int = Path(..., description="The ID of the website"),
        session_id: str = Query("default", description="Session ID to reset"),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Reset the conversation history for a session.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    success = rag_service.reset_conversation(session_id)
    return {"success": success}


@router.get("/{website_id}/feedback", response_model=Dict[str, Any])
def get_feedback_options(
        website_id: int = Path(..., description="The ID of the website"),
        website_repository: WebsiteRepository = Depends(get_website_repository)
):
    """
    Get available feedback options for responses.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    return {
        "rating_options": [
            {"value": "helpful", "label": "Helpful"},
            {"value": "somewhat_helpful", "label": "Somewhat Helpful"},
            {"value": "not_helpful", "label": "Not Helpful"},
        ],
        "feedback_categories": [
            {"value": "incorrect", "label": "Incorrect Information"},
            {"value": "incomplete", "label": "Incomplete Answer"},
            {"value": "irrelevant", "label": "Irrelevant Answer"},
            {"value": "too_complex", "label": "Too Complex"},
            {"value": "too_simple", "label": "Too Simple"},
            {"value": "other", "label": "Other"}
        ]
    }


@router.post("/{website_id}/feedback", response_model=Dict[str, bool])
async def submit_feedback(
        website_id: int = Path(..., description="The ID of the website"),
        conversation_id: int = Query(..., description="The ID of the conversation"),
        message_id: int = Query(..., description="The ID of the message"),
        rating: str = Query(..., description="Rating (helpful, somewhat_helpful, not_helpful)"),
        category: Optional[str] = Query(None, description="Feedback category"),
        comment: Optional[str] = Query(None, description="Feedback comment"),
        website_repository: WebsiteRepository = Depends(get_website_repository),
        background_tasks: BackgroundTasks = None
):
    """
    Submit feedback for a response.
    """
    # Check if website exists
    website = website_repository.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # In a background task, we would store this feedback in the database
    # and potentially use it for analytics or model improvement
    background_tasks.add_task(
        save_feedback,
        website_id=website_id,
        conversation_id=conversation_id,
        message_id=message_id,
        rating=rating,
        category=category,
        comment=comment
    )

    return {"success": True}


async def save_conversation_and_messages(
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        website_id: int,
        session_id: str,
        query: str,
        result: Dict[str, Any],
        user_info: Dict[str, Any] = None
):
    """Save the conversation and messages to the database."""
    try:
        # Get or create conversation
        conversation = conversation_repository.get_by_session_id(session_id)
        if not conversation:
            meta = {}
            if user_info:
                meta["user_info"] = user_info

            conversation = conversation_repository.create({
                "website_id": website_id,
                "session_id": session_id,
                "conversation_metadata": meta  # Changed from "metadata" to "conversation_metadata"
            })

        # Save user message
        user_message = message_repository.create({
            "conversation_id": conversation.id,
            "content": query,
            "is_user_message": True
        })

        # Save assistant message
        sources_json = json.dumps([{
            "url": source["url"],
            "title": source["title"]
        } for source in result.get("sources", [])])

        assistant_message = message_repository.create({
            "conversation_id": conversation.id,
            "content": result["answer"],
            "is_user_message": False,
            "sources": sources_json
        })
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")

async def save_feedback(
        website_id: int,
        conversation_id: int,
        message_id: int,
        rating: str,
        category: Optional[str] = None,
        comment: Optional[str] = None
):
    """Save feedback for a response (placeholder function)."""
    # In a real implementation, this would save to a feedback table
    # For now, we'll just log it
    feedback_data = {
        "website_id": website_id,
        "conversation_id": conversation_id,
        "message_id": message_id,
        "rating": rating,
        "category": category,
        "comment": comment,
        "timestamp": str(datetime.datetime.now())
    }

    # This would save to database in real implementation
    print(f"Received feedback: {json.dumps(feedback_data)}")
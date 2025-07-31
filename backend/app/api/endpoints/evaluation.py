from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, status
from app.services.evaluation_service import EvaluationService
from app.services.rag_service import RAGService

router = APIRouter()

# Create singleton instances of services
evaluation_service = EvaluationService()
rag_service = RAGService()


@router.post("/evaluate", response_model=Dict[str, Any])
def evaluate_answer(
        question: str = Body(..., description="The original question"),
        answer: str = Body(..., description="The generated answer"),
        context: Optional[str] = Body(None, description="The context used to generate the answer"),
        reference_answer: Optional[str] = Body(None, description="A reference answer to compare against")
):
    """
    Evaluate the quality of an answer.
    """
    return evaluation_service.evaluate_answer(
        question=question,
        answer=answer,
        context=context,
        reference_answer=reference_answer
    )


@router.post("/evaluate/session", response_model=Dict[str, Any])
def evaluate_session(
        website_id: int = Body(..., description="The ID of the website"),
        session_id: str = Body(..., description="The session ID"),
        num_samples: int = Body(5, description="Number of message pairs to evaluate")
):
    """
    Evaluate the quality of a conversation session.
    """
    # This is a placeholder - in a real implementation, you would:
    # 1. Retrieve the conversation history for the session
    # 2. Select a sample of question-answer pairs
    # 3. Evaluate each pair
    # 4. Aggregate the results

    return {
        "website_id": website_id,
        "session_id": session_id,
        "num_samples": num_samples,
        "average_score": 85.0,  # Example score
        "metrics": {
            "relevance": 90.0,
            "factuality": 85.0,
            "conciseness": 80.0
        },
        "samples": [
            {
                "question": "Example question 1",
                "answer": "Example answer 1",
                "score": 85.0
            },
            {
                "question": "Example question 2",
                "answer": "Example answer 2",
                "score": 90.0
            }
        ]
    }
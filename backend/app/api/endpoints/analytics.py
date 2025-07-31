from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.repositories.website import WebsiteRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.repositories.embedding_job import EmbeddingJobRepository
from app.api.dependencies import get_website_repository, get_current_active_user, get_current_active_superuser

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_stats(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get overall dashboard statistics.
    """
    # Create repository instances
    website_repo = WebsiteRepository(db)
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    embedding_job_repo = EmbeddingJobRepository(db)

    # Get basic stats
    website_count = len(website_repo.get_all())
    conversation_count = len(conversation_repo.get_all())
    message_count = len(message_repo.get_all())

    # Get active jobs
    embedding_jobs = embedding_job_repo.get_all()
    active_jobs = [job for job in embedding_jobs if job.status == "running"]
    recent_jobs = embedding_jobs[:10]  # Get 10 most recent jobs

    # Get stats by status
    jobs_by_status = {
        "completed": len([j for j in embedding_jobs if j.status == "completed"]),
        "failed": len([j for j in embedding_jobs if j.status == "failed"]),
        "pending": len([j for j in embedding_jobs if j.status == "pending"]),
        "running": len(active_jobs)
    }

    # Calculate success rate
    total_completed_jobs = jobs_by_status["completed"] + jobs_by_status["failed"]
    success_rate = 0
    if total_completed_jobs > 0:
        success_rate = (jobs_by_status["completed"] / total_completed_jobs) * 100

    return {
        "websites": {
            "total": website_count,
            "active": len(website_repo.get_active_websites())
        },
        "conversations": {
            "total": conversation_count,
            "last_24h": len([c for c in conversation_repo.get_all() if
                             (datetime.now() - c.created_at).total_seconds() < 86400])
        },
        "messages": {
            "total": message_count,
            "last_24h": len([m for m in message_repo.get_all() if
                             (datetime.now() - m.created_at).total_seconds() < 86400])
        },
        "jobs": {
            "active": len(active_jobs),
            "by_status": jobs_by_status,
            "success_rate": success_rate,
            "recent": [job.to_dict() for job in recent_jobs]
        }
    }


@router.get("/websites/{website_id}", response_model=Dict[str, Any])
def get_website_analytics(
        website_id: int = Path(..., description="The ID of the website"),
        days: int = 30,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get analytics for a specific website.
    """
    # Create repository instances
    website_repo = WebsiteRepository(db)
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)

    # Check if website exists
    website = website_repo.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # Get conversations for this website
    conversations = conversation_repo.get_by_website_id(website_id)

    # Calculate time period
    time_threshold = datetime.now() - timedelta(days=days)

    # Filter by time period
    recent_conversations = [c for c in conversations if c.created_at > time_threshold]

    # Get messages for these conversations
    conversation_ids = [c.id for c in recent_conversations]
    messages = []
    for conv_id in conversation_ids:
        messages.extend(message_repo.get_by_conversation_id(conv_id))

    # Calculate daily stats
    daily_stats = {}
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_stats[date] = {
            "conversations": 0,
            "messages": 0
        }

    for conv in recent_conversations:
        date = conv.created_at.strftime("%Y-%m-%d")
        if date in daily_stats:
            daily_stats[date]["conversations"] += 1

    for msg in messages:
        date = msg.created_at.strftime("%Y-%m-%d")
        if date in daily_stats:
            daily_stats[date]["messages"] += 1

    # Format for chart display
    daily_data = [
        {
            "date": date,
            "conversations": stats["conversations"],
            "messages": stats["messages"]
        }
        for date, stats in daily_stats.items()
    ]

    # Sort by date
    daily_data.sort(key=lambda x: x["date"])

    # Calculate stats for user vs. system messages
    user_messages = len([m for m in messages if m.is_user_message])
    system_messages = len(messages) - user_messages

    return {
        "website": {
            "id": website.id,
            "name": website.name,
            "url": website.url
        },
        "conversations": {
            "total": len(recent_conversations),
            "daily": daily_data
        },
        "messages": {
            "total": len(messages),
            "user": user_messages,
            "system": system_messages
        }
    }


@router.get("/crawling", response_model=Dict[str, Any])
def get_crawling_stats(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get statistics about crawling jobs.
    """
    # This would connect to the crawler service to get real-time data
    # For now, we'll return mock data that's representative

    return {
        "active_jobs": [
            {
                "id": "job-123",
                "website_id": 1,
                "website_name": "Example Website",
                "status": "running",
                "progress": 65,
                "urls_processed": 65,
                "urls_total": 100,
                "start_time": (datetime.now() - timedelta(minutes=30)).isoformat()
            }
        ],
        "recent_jobs": [
            {
                "id": "job-122",
                "website_id": 2,
                "website_name": "Documentation Site",
                "status": "completed",
                "urls_processed": 250,
                "urls_total": 250,
                "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "end_time": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                "id": "job-121",
                "website_id": 1,
                "website_name": "Example Website",
                "status": "failed",
                "urls_processed": 20,
                "urls_total": 100,
                "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
                "end_time": (datetime.now() - timedelta(days=1) + timedelta(minutes=15)).isoformat(),
                "error": "Connection timeout"
            }
        ],
        "stats": {
            "success_rate": 85,
            "average_duration_minutes": 45,
            "average_pages_per_minute": 5.5
        }
    }


@router.get("/content-coverage/{website_id}", response_model=Dict[str, Any])
def get_content_coverage(
        website_id: int = Path(..., description="The ID of the website"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get content coverage statistics for a website.
    """
    # Create repository instances
    website_repo = WebsiteRepository(db)

    # Check if website exists
    website = website_repo.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # In a real implementation, we would calculate these metrics
    # from the actual database records

    return {
        "pages": {
            "total": 120,
            "crawled": 110,
            "indexed": 105,
            "coverage_percentage": 87.5,
        },
        "by_content_type": [
            {"type": "blog", "count": 45, "percentage": 37.5},
            {"type": "documentation", "count": 65, "percentage": 54.2},
            {"type": "product", "count": 10, "percentage": 8.3}
        ],
        "by_section": [
            {"section": "/docs", "pages": 65, "coverage": 95},
            {"section": "/blog", "pages": 45, "coverage": 100},
            {"section": "/products", "pages": 10, "coverage": 80}
        ]
    }


@router.get("/performance", response_model=Dict[str, Any])
def get_performance_metrics(
        days: int = 7,
        current_user: User = Depends(get_current_active_superuser),
        db: Session = Depends(get_db)
):
    """
    Get system performance metrics.
    """
    # Generate mock data for performance metrics
    response_times = []
    embedding_times = []
    crawling_speeds = []

    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        response_times.append({
            "date": date,
            "avg_time_ms": 150 + (i * 10) + (30 - i * 5)  # Some variation
        })

        embedding_times.append({
            "date": date,
            "avg_time_s": 2.5 + (i * 0.3) - (0.2 * i)  # Some variation
        })

        crawling_speeds.append({
            "date": date,
            "pages_per_minute": 5.0 + (i * 0.5) - (0.3 * i)  # Some variation
        })

    # Sort by date
    response_times.sort(key=lambda x: x["date"])
    embedding_times.sort(key=lambda x: x["date"])
    crawling_speeds.sort(key=lambda x: x["date"])

    return {
        "response_times": {
            "current_avg_ms": 150,
            "history": response_times
        },
        "embedding_times": {
            "current_avg_s": 2.5,
            "history": embedding_times
        },
        "crawling_speeds": {
            "current_avg_pages_per_minute": 5.0,
            "history": crawling_speeds
        },
        "system_health": {
            "cpu_usage": 35,
            "memory_usage": 45,
            "disk_usage": 30,
            "status": "healthy"
        }
    }


@router.get("/top-queries/{website_id}", response_model=List[Dict[str, Any]])
def get_top_queries(
        website_id: int = Path(..., description="The ID of the website"),
        limit: int = 10,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get top queries for a website.
    """
    # Check if website exists
    website_repo = WebsiteRepository(db)
    website = website_repo.get(website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with ID {website_id} not found"
        )

    # This would actually analyze the conversation history
    # For now, return representative mock data

    return [
        {"query": "How do I reset my password?", "count": 25, "avg_rating": 4.5},
        {"query": "What are your pricing plans?", "count": 18, "avg_rating": 4.2},
        {"query": "How to cancel subscription", "count": 15, "avg_rating": 3.8},
        {"query": "Contact customer support", "count": 12, "avg_rating": 4.0},
        {"query": "Where is my order?", "count": 10, "avg_rating": 3.5},
        {"query": "How to return a product", "count": 8, "avg_rating": 4.3},
        {"query": "Shipping information", "count": 7, "avg_rating": 4.7},
        {"query": "What payment methods do you accept?", "count": 6, "avg_rating": 5.0},
        {"query": "How to create an account", "count": 5, "avg_rating": 4.2},
        {"query": "Where are you located?", "count": 4, "avg_rating": 4.0}
    ]
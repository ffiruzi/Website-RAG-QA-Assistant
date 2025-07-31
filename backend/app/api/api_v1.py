from fastapi import APIRouter
from app.api.endpoints import (
    websites,
    crawler,
    embeddings,
    qa,
    conversations,
    prompts,
    evaluation,
    auth,
    webhooks,
    users,
    auth_token,
    analytics,  # Add this line
)

api_router = APIRouter()

# The order matters - add auth first
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(auth_token.router, prefix="/token", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(websites.router, prefix="/websites", tags=["websites"])
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"])
api_router.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])  # Add this line
from fastapi import APIRouter
from app.api.endpoints import websites, crawler, embeddings, qa, conversations, prompts, evaluation

api_router = APIRouter()

api_router.include_router(websites.router, prefix="/websites", tags=["websites"])
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"])
api_router.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])
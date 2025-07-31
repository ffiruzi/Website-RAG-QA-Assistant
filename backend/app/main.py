from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.api.api_v1 import api_router as api_v1_router
from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.db.init_db import init_db
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.core.logger import setup_logging

# Set up logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_format=settings.LOG_FORMAT,
    log_file=settings.LOG_FILE
)

logger = logging.getLogger(__name__)

# Create tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Website RAG Q&A API",
    description="""
    API for the Website RAG Q&A System, a powerful tool that enables website owners to add intelligent 
    question-answering capabilities to their sites using Retrieval-Augmented Generation (RAG).

    ## Features

    * **Website Management**: Add, update, and delete websites to be crawled
    * **Content Crawling**: Automated extraction of content from websites
    * **Vector Embeddings**: Store and search content using vector embeddings
    * **RAG-Powered Answers**: Generate accurate answers based on website content
    * **Conversation History**: Track and manage user conversations

    ## Authentication

    This API uses OAuth2 with JWT tokens for authentication. To use authenticated endpoints, 
    you need to:

    1. Register a user account using the `/api/v1/auth/register` endpoint
    2. Obtain a JWT token using the `/api/v1/auth/login` endpoint
    3. Include the token in the `Authorization` header of your requests: `Bearer {token}`

    ## Rate Limiting

    To ensure fair usage, API requests are limited to {settings.RATE_LIMIT_PER_MINUTE} per minute 
    per client. Rate limit information is included in the response headers:

    * `X-RateLimit-Limit`: Maximum requests per minute
    * `X-RateLimit-Remaining`: Remaining requests in the current minute
    * `X-RateLimit-Reset`: Seconds until the rate limit resets

    ## API Versioning

    This API supports versioning to ensure backward compatibility. The current version 
    is accessible at `/api/v1/`. Legacy endpoints at `/api/` will be deprecated in future versions.
    """,
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middlewares
# app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include versioned API router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
# Import the simple auth router for testing
from app.api.endpoints import auth_simple

# Add the simple auth router
app.include_router(auth_simple.router, prefix="/api/v1/auth-simple", tags=["auth-simple"])

# Legacy unversioned router - for backward compatibility
# This will be deprecated in future versions
app.include_router(api_v1_router, prefix="/api")


# Include versioned API router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

# Legacy unversioned router - for backward compatibility
# This will be deprecated in future versions
app.include_router(api_v1_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Website RAG Q&A API",
        "version": "0.1.0",
        "documentation": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"/api/v1/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=f"/api/v1/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/api/v1/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=f"/api/v1/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


@app.get("/api/v1/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    """
    Get custom OpenAPI schema with improved documentation
    """
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add more information to the schema
    openapi_schema["info"]["contact"] = {
        "name": "Support",
        "email": "support@example.com",
        "url": "https://example.com/support"
    }

    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": f"{settings.API_V1_PREFIX}/auth/login",
                    "scopes": {}
                }
            }
        }
    }

    # Apply security to all operations
    if "security" not in openapi_schema:
        openapi_schema["security"] = []

    openapi_schema["security"].append({"OAuth2PasswordBearer": []})

    return openapi_schema


# Direct login endpoint for testing
@app.post("/direct-login")
def direct_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Direct login endpoint for testing."""
    return {"message": "Login endpoint reached", "username": form_data.username}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )


@app.on_event("startup")
async def startup_event():
    logger.info("Starting application")
    db = next(get_db())
    init_db(db)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
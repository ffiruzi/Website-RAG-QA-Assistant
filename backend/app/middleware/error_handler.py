import logging
import traceback
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except SQLAlchemyError as e:
            # Handle database errors
            logger.error(
                "Database error",
                extra={
                    "error": str(e),
                    "path": request.url.path,
                    "method": request.method,
                    "traceback": traceback.format_exc()
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal database error occurred",
                    "error_code": "DATABASE_ERROR"
                }
            )
        except Exception as e:
            # Handle any other exceptions
            logger.error(
                "Unhandled exception",
                extra={
                    "error": str(e),
                    "path": request.url.path,
                    "method": request.method,
                    "traceback": traceback.format_exc()
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal server error occurred",
                    "error_code": "INTERNAL_SERVER_ERROR"
                }
            )
import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log the request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )

        # Record the start time
        start_time = time.time()

        # Process the request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log the response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2)
                }
            )

            # Add the request ID to the response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log the error
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time_ms": round((time.time() - start_time) * 1000, 2)
                },
                exc_info=True
            )

            # Re-raise the exception
            raise
import time
from typing import Dict, Set, Tuple, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings


# Simple in-memory rate limiter (use Redis in production)
class RateLimiter:
    def __init__(self, limit_per_minute: int = 60):
        self.limit_per_minute = limit_per_minute
        self.requests: Dict[str, Set[float]] = {}  # client_id -> set of timestamps

    def is_rate_limited(self, client_id: str) -> Tuple[bool, Optional[int]]:
        current_time = time.time()
        minute_ago = current_time - 60

        # Create a set for this client if it doesn't exist
        if client_id not in self.requests:
            self.requests[client_id] = set()

        # Remove timestamps older than 1 minute
        self.requests[client_id] = {ts for ts in self.requests[client_id] if ts > minute_ago}

        # Check if the client has reached the limit
        if len(self.requests[client_id]) >= self.limit_per_minute:
            # Calculate time until reset
            oldest_timestamp = min(self.requests[client_id]) if self.requests[client_id] else minute_ago
            reset_time = int(60 - (current_time - oldest_timestamp))
            return True, reset_time

        # Add the current timestamp to the set
        self.requests[client_id].add(current_time)
        return False, None


# Create a singleton instance of the rate limiter
rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        if request.url.path.startswith("/docs") or request.url.path.startswith(
                "/redoc") or request.url.path == "/health":
            return await call_next(request)

        # Identify the client - use API key if available, otherwise use IP
        client_id = request.headers.get("X-API-Key", request.client.host)

        # Check if the client is rate limited
        is_limited, reset_time = rate_limiter.is_rate_limited(client_id)

        if is_limited:
            headers = {
                "Retry-After": str(reset_time),
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                "X-RateLimit-Reset": str(reset_time)
            }
            return Response(
                content="Rate limit exceeded. Try again later.",
                status_code=429,
                headers=headers
            )

        response = await call_next(request)

        # Add rate limit headers to the response
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(
            settings.RATE_LIMIT_PER_MINUTE - len(rate_limiter.requests.get(client_id, set()))
        )

        return response
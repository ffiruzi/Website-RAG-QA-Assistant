from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class NotFoundError(HTTPException):
    """Resource not found error."""

    def __init__(
            self,
            detail: str = "Resource not found",
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers
        )


class BadRequestError(HTTPException):
    """Bad request error."""

    def __init__(
            self,
            detail: str = "Bad request",
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers
        )


class UnauthorizedError(HTTPException):
    """Unauthorized error."""

    def __init__(
            self,
            detail: str = "Not authenticated",
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers
        )


class ForbiddenError(HTTPException):
    """Forbidden error."""

    def __init__(
            self,
            detail: str = "Not enough permissions",
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers
        )


class ConflictError(HTTPException):
    """Conflict error."""

    def __init__(
            self,
            detail: str = "Resource conflict",
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers=headers
        )


class RateLimitError(HTTPException):
    """Rate limit error."""

    def __init__(
            self,
            detail: str = "Rate limit exceeded",
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers
        )


class ServiceUnavailableError(HTTPException):
    """Service unavailable error."""

    def __init__(
            self,
            detail: str = "Service unavailable",
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers
        )
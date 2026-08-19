"""
shared/exceptions.py
--------------------
Shared custom exception hierarchy used across all backend services.
"""

from __future__ import annotations


class AppException(Exception):
    """
    Base application exception.

    Raise this (or a subclass) anywhere in the business logic layer.
    The global exception handler registered in each service's ``app/main.py``
    will intercept it and return a unified JSON error response:

        {"success": false, "error": "<message>"}

    Attributes:
        message: Human-readable error description surfaced to the API caller.
        status_code: HTTP status code for the response (default 400).
    """

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppException):
    """Raised when a required resource or artifact is missing."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ServiceUnavailableError(AppException):
    """Raised when a downstream dependency (DB, model, etc.) is not ready."""

    def __init__(self, message: str = "Service temporarily unavailable") -> None:
        super().__init__(message, status_code=503)


class UnauthorizedError(AppException):
    """Raised when request authentication fails."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=401)

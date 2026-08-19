"""
embedding_service/app/config/error_handler.py
----------------------------------------------
Global exception handler registration for the Embedding Service.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shared.exceptions import AppException

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to *app*."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "AppException [%s %s] status=%d message=%r",
            request.method,
            request.url.path,
            exc.status_code,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        logger.warning("Validation error [%s %s]: %s", request.method, request.url.path, errors)
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Request validation failed.",
                "detail": errors,
            },
        )

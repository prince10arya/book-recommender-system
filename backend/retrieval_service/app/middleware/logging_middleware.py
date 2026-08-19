"""
retrieval_service/app/middleware/logging_middleware.py
-------------------------------------------------------
Custom ASGI middleware that measures wall-clock request processing time
and appends it to every response as the ``X-Process-Time`` header.
"""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware — records elapsed seconds for each request and exposes
    it via the ``X-Process-Time`` response header (value in seconds, 6 d.p.).
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"
        return response

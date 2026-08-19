"""
retrieval_service/app/services/auth_service.py
-----------------------------------------------
Token-based authentication guard for the Retrieval Service.

The Retrieval Service is the public-facing API consumed by the frontend.
Token verification is provided here as an **optional per-route dependency**
rather than enforced globally, so unauthenticated GET /recommend calls from
the browser remain unblocked.

Set ``REQUIRE_TOKEN=true`` in your environment to enable token enforcement
on the recommendation endpoint.

Usage (opt-in per route)::

    from retrieval_service.app.services.auth_service import verify_token

    @router.post("/recommend", dependencies=[Depends(verify_token)])
    async def recommend(): ...
"""

from __future__ import annotations

import os

from fastapi import Header, HTTPException, status

_SERVICE_TOKEN: str = os.getenv("SERVICE_TOKEN", "dev-secret-token")
_REQUIRE_TOKEN: bool = os.getenv("REQUIRE_TOKEN", "false").lower() == "true"


async def verify_token(x_token: str | None = Header(default=None, alias="X-Token")) -> None:
    """
    FastAPI dependency — optionally validate the ``X-Token`` request header.

    When ``REQUIRE_TOKEN`` is false (default) this is a no-op, allowing the
    frontend to call the public API without credentials.

    Raises:
        HTTPException(401): only when ``REQUIRE_TOKEN=true`` and token mismatches.
    """
    if not _REQUIRE_TOKEN:
        return
    if x_token != _SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Token header.",
        )

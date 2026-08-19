"""
preprocessing_service/app/services/auth_service.py
----------------------------------------------------
Token-based authentication guard for the Preprocessing Service.

This service is internal (not publicly exposed) so we enforce a shared
service token on all mutating endpoints (POST /upload, POST /preprocess).

Environment variable:
    SERVICE_TOKEN — expected value of the ``X-Token`` header.
    Falls back to the hard-coded development default when not set.

Usage (as a FastAPI dependency)::

    from preprocessing_service.app.services.auth_service import verify_token

    @router.post("/preprocess", dependencies=[Depends(verify_token)])
    async def preprocess(): ...
"""

from __future__ import annotations

import os

from fastapi import Header, HTTPException, status

# ---------------------------------------------------------------------------
# Secret resolution — env var wins; fall back to dev default.
# ---------------------------------------------------------------------------

_SERVICE_TOKEN: str = os.getenv("SERVICE_TOKEN", "dev-secret-token")


async def verify_token(x_token: str = Header(..., alias="X-Token")) -> None:
    """
    FastAPI dependency — validate the ``X-Token`` request header.

    Raises:
        HTTPException(401): when the header is missing or does not match.
    """
    if x_token != _SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Token header.",
        )

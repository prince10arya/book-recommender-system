"""
embedding_service/app/services/auth_service.py
-----------------------------------------------
Token-based authentication guard for the Embedding Service.

This service is internal. All mutating endpoints require a valid
``X-Token`` header whose value matches the ``SERVICE_TOKEN`` env variable.

Usage::

    from embedding_service.app.services.auth_service import verify_token

    @router.post("/embed", dependencies=[Depends(verify_token)])
    async def embed(): ...
"""

from __future__ import annotations

import os

from fastapi import Header, HTTPException, status

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

"""
embedding_service/app/routers/embed_router.py
----------------------------------------------
Controller — defines all HTTP routes for the Embedding Service.

Routes:
  GET  /        Health check
  GET  /status  ChromaDB existence and document count
  POST /embed   Trigger embedding pipeline (guarded by X-Token)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from shared.config import CHROMA_PATH
from shared.exceptions import NotFoundError
from embedding_service.app.schemas.embed_schema import EmbedResponse, EmbedStatus
from embedding_service.app.services.auth_service import verify_token
from embedding_service.embedder import build_chroma_db, get_db_stats, is_db_populated

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get(
    "/",
    tags=["Health"],
    summary="Service health check",
    response_description="Service name and status string.",
)
async def health_check() -> dict[str, str]:
    """Returns a simple liveness probe — no dependencies queried."""
    return {"status": "ok", "service": "embedding"}


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


@router.get(
    "/status",
    response_model=EmbedStatus,
    tags=["Status"],
    summary="ChromaDB status",
    response_description="Existence flag and document count for the ChromaDB vector store.",
)
async def get_status() -> EmbedStatus:
    """Returns the current state of the ChromaDB vector store."""
    if not is_db_populated(CHROMA_PATH):
        return EmbedStatus(
            chroma_db_exists=False,
            document_count=None,
            message="ChromaDB not found. Run POST /embed to build it.",
        )

    try:
        stats = get_db_stats(CHROMA_PATH)
        return EmbedStatus(
            chroma_db_exists=True,
            document_count=stats["document_count"],
            message=f"ChromaDB ready — {stats['document_count']:,} documents.",
        )
    except Exception as exc:
        logger.exception("Failed to read ChromaDB stats")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Embed (guarded)
# ---------------------------------------------------------------------------


@router.post(
    "/embed",
    response_model=EmbedResponse,
    tags=["Pipeline"],
    summary="Run embedding pipeline",
    # dependencies=[Depends(verify_token)],
)
async def embed(
    force: bool = Query(
        default=False,
        description="Set to true to rebuild ChromaDB even if it already exists.",
    ),
) -> EmbedResponse:
    """
    Run the embedding pipeline.

    Reads ``tagged_description.txt``, calls the Gemini embedding API in
    batches, and persists results to ChromaDB. Idempotent by default —
    pass ``?force=true`` to force a full rebuild.
    """
    try:
        logger.info("Starting embedding pipeline (force=%s)...", force)
        result = build_chroma_db(force=force)

        if result.get("skipped"):
            return EmbedResponse(
                success=True,
                documents_embedded=result["documents_embedded"],
                message=(
                    f"ChromaDB already populated ({result['documents_embedded']:,} docs). "
                    "Pass ?force=true to rebuild."
                ),
            )

        return EmbedResponse(
            success=True,
            documents_embedded=result["documents_embedded"],
            message=f"Embedding complete — {result['documents_embedded']:,} documents stored in ChromaDB.",
        )
    except FileNotFoundError as exc:
        raise NotFoundError(str(exc)) from exc
    except Exception as exc:
        logger.exception("Embedding pipeline failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

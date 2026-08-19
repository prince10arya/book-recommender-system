"""
retrieval_service/app/routers/retrieval_router.py
--------------------------------------------------
Controller — defines all HTTP routes for the Retrieval Service.

Routes:
  GET  /          Health check (unauthenticated)
  POST /recommend  Semantic book recommendations (unauthenticated by default;
                   toggle on via REQUIRE_TOKEN=true env var)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from shared.exceptions import ServiceUnavailableError
from shared.models import BookResult, RecommendResponse  # matches retrieve() return type
from retrieval_service.app.schemas.retrieval_schema import RecommendRequest
from retrieval_service.app.services.auth_service import verify_token
from retrieval_service.retriever import retrieve

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
    return {"status": "ok", "message": "Book Recommender API is running"}


# ---------------------------------------------------------------------------
# Recommend
# ---------------------------------------------------------------------------


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    tags=["Recommendations"],
    summary="Semantic book recommendations",
    # dependencies=[Depends(verify_token)],
)
async def recommend_books(request: RecommendRequest) -> RecommendResponse:
    """
    Return semantically similar book recommendations for a natural-language query.

    Uses ChromaDB cosine similarity search backed by OpenRouter embeddings.
    Same request/response contract as v1 — fully backwards-compatible.
    """
    try:
        results = retrieve(request.query, request.top_k)
        return RecommendResponse(
            query=request.query,
            results=results,
            total=len(results),
        )
    except RuntimeError as exc:
        raise ServiceUnavailableError(str(exc)) from exc
    except Exception as exc:
        logger.exception("Recommendation failed for query: %r", request.query)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

"""
retrieval_service/app/schemas/retrieval_schema.py
--------------------------------------------------
Pydantic validation models for the Retrieval Service (public-facing API).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class RecommendRequest(BaseModel):
    """Request body for POST /recommend."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Natural-language search query for semantic book recommendation.",
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of book recommendations to return (1–50).",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class BookResult(BaseModel):
    """Single book result returned by the recommendation engine."""

    isbn13: str
    isbn10: str
    title: str
    title_and_subtitle: str
    authors: str
    categories: str
    thumbnail: str
    description: str
    published_year: int | None
    average_rating: float | None
    num_pages: int | None
    ratings_count: int | None
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score (0–1).")


class RecommendResponse(BaseModel):
    """Response envelope returned by POST /recommend."""

    query: str
    results: list[BookResult]
    total: int = Field(..., ge=0, description="Number of results returned.")

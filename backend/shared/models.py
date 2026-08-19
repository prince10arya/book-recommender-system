"""
shared/models.py
----------------
Pydantic request/response models shared across all three services.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Retrieval Service models
# ---------------------------------------------------------------------------


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural-language search query")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to return")


class BookResult(BaseModel):
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
    similarity_score: float


class RecommendResponse(BaseModel):
    query: str
    results: list[BookResult]
    total: int


# ---------------------------------------------------------------------------
# Preprocessing Service models
# ---------------------------------------------------------------------------


class PreprocessStatus(BaseModel):
    cleaned_csv_exists: bool
    tagged_txt_exists: bool
    row_count: int | None = None
    message: str


class PreprocessResponse(BaseModel):
    success: bool
    rows_processed: int
    rows_after_clean: int
    message: str


class UploadResponse(BaseModel):
    success: bool
    filename: str
    rows: int
    size_kb: int
    message: str


# ---------------------------------------------------------------------------
# Embedding Service models
# ---------------------------------------------------------------------------


class EmbedStatus(BaseModel):
    chroma_db_exists: bool
    document_count: int | None = None
    message: str


class EmbedResponse(BaseModel):
    success: bool
    documents_embedded: int
    message: str

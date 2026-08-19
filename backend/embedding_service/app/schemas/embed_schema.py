"""
embedding_service/app/schemas/embed_schema.py
----------------------------------------------
Pydantic validation models for the Embedding Service.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class EmbedRequest(BaseModel):
    """Optional request body for POST /embed."""

    force: bool = Field(
        default=False,
        description=(
            "Set to true to rebuild ChromaDB even if it is already populated. "
            "Triggers a full re-embedding of all documents."
        ),
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class EmbedStatus(BaseModel):
    """Current state of the ChromaDB vector store."""

    chroma_db_exists: bool
    document_count: int | None = Field(
        default=None,
        description="Total documents stored in ChromaDB (null when not yet created).",
    )
    message: str


class EmbedResponse(BaseModel):
    """Result returned by POST /embed after the pipeline completes."""

    success: bool
    documents_embedded: int = Field(..., ge=0, description="Number of documents written to ChromaDB.")
    message: str

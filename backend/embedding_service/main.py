"""
embedding_service/main.py
--------------------------
FastAPI application for the Embedding Service (port 8002).

Endpoints:
  GET  /       → health check
  GET  /status → ChromaDB existence and document count
  POST /embed  → trigger embedding pipeline (optional ?force=true to rebuild)
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from shared.config import CHROMA_PATH
from shared.models import EmbedResponse, EmbedStatus
from embedding_service.embedder import build_chroma_db, get_db_stats, is_db_populated

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book Recommender — Embedding Service",
    description="Generates Gemini embeddings and populates ChromaDB.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "embedding"}


@app.get("/status", response_model=EmbedStatus, tags=["Status"])
async def get_status():
    """
    Returns the current state of the ChromaDB vector store.
    """
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
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/embed", response_model=EmbedResponse, tags=["Pipeline"])
async def embed(
    force: bool = Query(
        default=False,
        description="Set to true to rebuild ChromaDB even if it already exists.",
    )
):
    """
    Run the embedding pipeline.

    Reads `tagged_description.txt`, calls the Gemini embedding API in batches,
    and persists results to ChromaDB. Idempotent by default — pass `?force=true`
    to force a full rebuild.
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
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Embedding pipeline failed")
        raise HTTPException(status_code=500, detail=str(exc))

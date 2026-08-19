"""
retrieval_service/main.py
--------------------------
FastAPI application for the Retrieval Service (port 8000).

This is the public-facing service — the only one the frontend calls.
Contract is identical to the original backend, so zero frontend changes needed.

Endpoints:
  GET  /          → health check
  POST /recommend → semantic book recommendations
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared.models import RecommendRequest, RecommendResponse
from retrieval_service.retriever import initialize, retrieve

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ChromaDB and book metadata once — fail fast if artifacts are missing."""
    logger.info("Starting Retrieval Service — loading artifacts...")
    try:
        initialize()
    except RuntimeError as exc:
        # Log the error clearly; uvicorn will still start but /recommend will fail
        logger.error("Initialisation failed: %s", exc)
        logger.error(
            "Ensure the Preprocessing and Embedding services have been run first."
        )
    yield
    logger.info("Retrieval Service shutting down.")


app = FastAPI(
    title="Book Recommender API",
    description="Semantic book recommendations powered by ChromaDB + Google Generative AI Embeddings.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Book Recommender API is running"}


@app.post("/recommend", response_model=RecommendResponse, tags=["Recommendations"])
async def recommend_books(request: RecommendRequest):
    """
    Get semantically similar book recommendations for a natural-language query.

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
        # Service not ready (artifacts missing)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Recommendation failed for query: %r", request.query)
        raise HTTPException(status_code=500, detail=str(exc))

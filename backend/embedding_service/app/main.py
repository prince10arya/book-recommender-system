"""
embedding_service/app/main.py
------------------------------
Application entry point for the Embedding Service.

Responsibilities:
  1. Create the FastAPI instance with metadata
  2. Attach CORS middleware
  3. Attach the process-time logging middleware
  4. Register global exception handlers (AppException, validation errors)
  5. Mount the embedding router under the root prefix
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from embedding_service.app.config.error_handler import register_error_handlers
from embedding_service.app.middleware.logging_middleware import ProcessTimeMiddleware
from embedding_service.app.routers.embed_router import router as embed_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# FastAPI instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Book Recommender — Embedding Service",
    description=(
        "Generates Gemini embeddings and populates ChromaDB. "
        "Internal service — requires X-Token on the embedding trigger route."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware (outermost first)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom ASGI middleware — appends X-Process-Time to every response
app.add_middleware(ProcessTimeMiddleware)

# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

register_error_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(embed_router)

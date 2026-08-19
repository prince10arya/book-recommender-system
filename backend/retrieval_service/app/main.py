"""
retrieval_service/app/main.py
------------------------------
Application entry point for the Retrieval Service.

Responsibilities:
  1. Create the FastAPI instance with lifespan context (loads ChromaDB once)
  2. Attach CORS middleware (permissive for frontend access)
  3. Attach the process-time logging middleware
  4. Register global exception handlers (AppException, validation errors)
  5. Mount the retrieval router under the root prefix
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from retrieval_service.app.config.error_handler import register_error_handlers
from retrieval_service.app.middleware.logging_middleware import ProcessTimeMiddleware
from retrieval_service.app.routers.retrieval_router import router as retrieval_router
from retrieval_service.retriever import initialize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — load artifacts once at startup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ChromaDB and book metadata once — fail fast if artifacts are missing."""
    logger.info("Starting Retrieval Service — loading artifacts...")
    try:
        initialize()
    except RuntimeError as exc:
        logger.error("Initialisation failed: %s", exc)
        logger.error(
            "Ensure the Preprocessing and Embedding services have been run first."
        )
    yield
    logger.info("Retrieval Service shutting down.")


# ---------------------------------------------------------------------------
# FastAPI instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Book Recommender API",
    description=(
        "Semantic book recommendations powered by ChromaDB + Google Generative AI Embeddings. "
        "Public-facing service — the only endpoint the frontend calls."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware (outermost first)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
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

app.include_router(retrieval_router)

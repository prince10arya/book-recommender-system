"""
preprocessing_service/app/main.py
----------------------------------
Application entry point for the Preprocessing Service.

Responsibilities:
  1. Create the FastAPI instance with metadata
  2. Attach CORS middleware
  3. Attach the process-time logging middleware
  4. Register global exception handlers (AppException, validation errors)
  5. Mount the preprocessing router under the root prefix

All business logic, validation, and guards live in their respective
layers — this file is the wiring layer only.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from preprocessing_service.app.config.error_handler import register_error_handlers
from preprocessing_service.app.middleware.logging_middleware import ProcessTimeMiddleware
from preprocessing_service.app.routers.preprocess_router import router as preprocess_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# FastAPI instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Book Recommender — Preprocessing Service",
    description=(
        "ETL pipeline: cleans raw books CSV and produces artifacts "
        "for downstream services. Internal service — requires X-Token on mutating routes."
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

app.include_router(preprocess_router)

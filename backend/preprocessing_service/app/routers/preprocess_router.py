"""
preprocessing_service/app/routers/preprocess_router.py
--------------------------------------------------------
Controller — defines all HTTP routes for the Preprocessing Service.

Routes:
  GET  /         Health check
  GET  /status   Artifact existence and row-count summary
  POST /upload   Upload the raw books.csv to the shared data volume
  POST /preprocess  Run the full ETL pipeline (guarded by X-Token)

Token guard is applied to the two mutating endpoints so the health and
status probes remain unauthenticated (useful for Docker health checks and
monitoring).
"""

from __future__ import annotations

import logging
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from shared.config import CLEANED_CSV_PATH, RAW_CSV_PATH, TAGGED_TXT_PATH
from shared.exceptions import AppException, NotFoundError
from preprocessing_service.app.schemas.preprocess_schema import (
    PreprocessResponse,
    PreprocessStatus,
    UploadResponse,
)
from preprocessing_service.app.services.auth_service import verify_token
from preprocessing_service.preprocessor import run_pipeline

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
    return {"status": "ok", "service": "preprocessing"}


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


@router.get(
    "/status",
    response_model=PreprocessStatus,
    tags=["Status"],
    summary="Artifact status",
    response_description="Existence flags and row counts for data volume artifacts.",
)
async def get_status() -> PreprocessStatus:
    """Returns the current state of the data volume artifacts."""
    raw_exists = RAW_CSV_PATH.exists()
    cleaned_exists = CLEANED_CSV_PATH.exists()
    tagged_exists = TAGGED_TXT_PATH.exists()

    row_count: int | None = None
    if cleaned_exists:
        try:
            import pandas as pd  # noqa: PLC0415 — lazy import (heavy dep)

            row_count = len(pd.read_csv(CLEANED_CSV_PATH))
        except Exception:
            row_count = None

    msg_parts: list[str] = []
    if not raw_exists:
        msg_parts.append("books.csv not uploaded yet — call POST /upload first")
    else:
        msg_parts.append("books.csv ✓")
    if cleaned_exists:
        msg_parts.append(f"books_cleaned.csv ({row_count} rows) ✓")
    if tagged_exists:
        msg_parts.append("tagged_description.txt ✓")

    return PreprocessStatus(
        cleaned_csv_exists=cleaned_exists,
        tagged_txt_exists=tagged_exists,
        row_count=row_count,
        message=" · ".join(msg_parts) or "No artifacts found.",
    )


# ---------------------------------------------------------------------------
# Upload (guarded)
# ---------------------------------------------------------------------------


@router.post(
    "/upload",
    response_model=UploadResponse,
    tags=["Data"],
    summary="Upload raw books CSV",
    # dependencies=[Depends(verify_token)],
    status_code=status.HTTP_201_CREATED,
)
async def upload_csv(
    file: UploadFile = File(..., description="Raw books CSV (books.csv from Kaggle)"),
) -> UploadResponse:
    """
    Upload the raw books CSV to the shared data volume.

    Accepts the ``books.csv`` file from the Kaggle dataset
    (dylanjcastillo/7k-books-with-metadata). After uploading, call
    **POST /preprocess** to run the ETL pipeline.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise AppException(
            "Only .csv files are accepted. Please upload the Kaggle books.csv file.",
            status_code=400,
        )

    try:
        RAW_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with RAW_CSV_PATH.open("wb") as dest:
            shutil.copyfileobj(file.file, dest)

        import pandas as pd  # noqa: PLC0415

        df = pd.read_csv(RAW_CSV_PATH)
        row_count = len(df)
        size_kb = RAW_CSV_PATH.stat().st_size // 1024

        logger.info(
            "Uploaded %s → %s (%d rows, %d KB)", file.filename, RAW_CSV_PATH, row_count, size_kb
        )
        return UploadResponse(
            success=True,
            filename=file.filename,
            rows=row_count,
            size_kb=size_kb,
            message=f"Uploaded {file.filename} ({row_count:,} rows, {size_kb} KB). Now call POST /preprocess.",
        )
    except AppException:
        raise
    except Exception as exc:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        await file.close()


# ---------------------------------------------------------------------------
# Preprocess (guarded)
# ---------------------------------------------------------------------------


@router.post(
    "/preprocess",
    response_model=PreprocessResponse,
    tags=["Pipeline"],
    summary="Run ETL pipeline",
    # dependencies=[Depends(verify_token)],
)
async def preprocess() -> PreprocessResponse:
    """
    Run the full ETL pipeline.

    Reads ``books.csv`` (uploaded via POST /upload), cleans and filters the
    data, then writes ``books_cleaned.csv`` and ``tagged_description.txt``
    to the shared volume.
    """
    try:
        logger.info("Starting preprocessing pipeline...")
        stats = run_pipeline()
        logger.info("Pipeline complete: %s", stats)
        return PreprocessResponse(
            success=True,
            rows_processed=stats["rows_processed"],
            rows_after_clean=stats["rows_after_clean"],
            message=(
                f"Pipeline complete. {stats['rows_after_clean']:,} books ready "
                f"(from {stats['rows_processed']:,} raw rows)."
            ),
        )
    except FileNotFoundError as exc:
        raise NotFoundError(str(exc)) from exc
    except Exception as exc:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

"""
preprocessing_service/main.py
------------------------------
FastAPI application for the Preprocessing Service (port 8001).

Endpoints:
  GET  /         → health check
  GET  /status   → shows whether artifacts exist and their sizes
  POST /preprocess → runs the full ETL pipeline
"""

from __future__ import annotations

import logging
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from shared.config import CLEANED_CSV_PATH, RAW_CSV_PATH, TAGGED_TXT_PATH
from shared.models import PreprocessResponse, PreprocessStatus, UploadResponse
from preprocessing_service.preprocessor import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book Recommender — Preprocessing Service",
    description="ETL pipeline: cleans raw books CSV and produces artifacts for downstream services.",
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
    return {"status": "ok", "service": "preprocessing"}


@app.post("/upload", response_model=UploadResponse, tags=["Data"])
async def upload_csv(file: UploadFile = File(..., description="Raw books CSV (books.csv from Kaggle)")):
    """
    Upload the raw books CSV file to the data volume.

    Accepts the `books.csv` file downloaded from Kaggle
    (dylanjcastillo/7k-books-with-metadata) and saves it as `books.csv`
    on the shared data volume so the preprocessing pipeline can read it.

    After uploading, call **POST /preprocess** to clean and prepare the data.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are accepted. Please upload the Kaggle books.csv file.",
        )

    try:
        RAW_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with RAW_CSV_PATH.open("wb") as dest:
            shutil.copyfileobj(file.file, dest)

        # Quick sanity check — count rows
        import pandas as pd
        df = pd.read_csv(RAW_CSV_PATH)
        row_count = len(df)
        size_kb = RAW_CSV_PATH.stat().st_size // 1024

        logger.info("Uploaded %s → %s (%d rows, %d KB)", file.filename, RAW_CSV_PATH, row_count, size_kb)
        return UploadResponse(
            success=True,
            filename=file.filename,
            rows=row_count,
            size_kb=size_kb,
            message=f"Uploaded {file.filename} ({row_count:,} rows, {size_kb} KB). Now call POST /preprocess.",
        )
    except Exception as exc:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        await file.close()


@app.get("/status", response_model=PreprocessStatus, tags=["Status"])
async def get_status():
    """
    Returns the current state of the data volume artifacts.
    """
    raw_exists = RAW_CSV_PATH.exists()
    cleaned_exists = CLEANED_CSV_PATH.exists()
    tagged_exists = TAGGED_TXT_PATH.exists()

    row_count: int | None = None
    if cleaned_exists:
        try:
            import pandas as pd
            row_count = len(pd.read_csv(CLEANED_CSV_PATH))
        except Exception:
            row_count = None

    msg_parts = []
    if not raw_exists:
        msg_parts.append("books.csv not uploaded yet — call POST /upload first")
    else:
        msg_parts.append("books.csv ✓")
    if cleaned_exists:
        msg_parts.append(f"books_cleaned.csv ({row_count} rows) ✓")
    if tagged_exists:
        msg_parts.append("tagged_description.txt ✓")

    message = " · ".join(msg_parts) or "No artifacts found."

    return PreprocessStatus(
        cleaned_csv_exists=cleaned_exists,
        tagged_txt_exists=tagged_exists,
        row_count=row_count,
        message=message,
    )


@app.post("/preprocess", response_model=PreprocessResponse, tags=["Pipeline"])
async def preprocess():
    """
    Run the full ETL pipeline.

    Reads `books.csv` (uploaded via POST /upload), cleans and filters the data,
    then writes `books_cleaned.csv` and `tagged_description.txt` to the shared volume.
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
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=str(exc))

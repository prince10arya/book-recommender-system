"""
preprocessing_service/preprocessor.py
--------------------------------------
ETL pipeline: reads the raw books CSV, cleans it, and produces the two
artifacts consumed downstream:
  - books_cleaned.csv      → used by the Retrieval Service for metadata lookup
  - tagged_description.txt → used by the Embedding Service for vector ingestion

Logic formalised from data_exploration_and_preprocessing.ipynb.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from shared.config import (
    CLEANED_CSV_PATH,
    MIN_DESC_LENGTH,
    RAW_CSV_PATH,
    TAGGED_TXT_PATH,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Individual pipeline steps
# ---------------------------------------------------------------------------


def load_raw_csv(path: Path = RAW_CSV_PATH) -> pd.DataFrame:
    """Load the raw Kaggle books CSV into a DataFrame."""
    if not path.exists():
        raise FileNotFoundError(
            f"Raw CSV not found at {path}. "
            "Download it from Kaggle (dylanjcastillo/7k-books-with-metadata) "
            "and place it at the expected location."
        )
    df = pd.read_csv(path)
    logger.info("Loaded raw CSV: %d rows, %d columns", *df.shape)
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the same cleaning steps used in the exploration notebook:
    1. Drop rows missing description, num_pages, average_rating, or published_year.
    2. Keep only books whose description is at least MIN_DESC_LENGTH characters.
    3. Build `title_and_subtitle` (title + subtitle when present).
    4. Drop helper/temporary columns.
    """
    original_count = len(df)

    # Step 1: Drop rows with critical nulls
    df = df.dropna(subset=["description", "num_pages", "average_rating", "published_year"])

    # Step 2: Filter by description length
    df = df[df["description"].str.strip().str.len() >= MIN_DESC_LENGTH].copy()

    # Step 3: Composite title column
    df["title_and_subtitle"] = np.where(
        df["subtitle"].isna(),
        df["title"],
        df[["title", "subtitle"]].astype(str).agg(": ".join, axis=1),
    )

    # Step 4: Drop unused columns
    cols_to_drop = [c for c in ["subtitle", "missing_description", "age_of_book", "words_in_description"] if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    logger.info(
        "Cleaned: %d → %d rows (dropped %d)",
        original_count,
        len(df),
        original_count - len(df),
    )
    return df


def add_tagged_description(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a `tagged_description` column: "<isbn13> <description>".
    This is the format ingested by the Embedding Service.
    """
    df = df.copy()
    df["isbn13"] = df["isbn13"].astype(str)
    df["tagged_description"] = (
        df[["isbn13", "description"]].astype(str).agg(" ".join, axis=1)
    )
    return df


def save_cleaned_csv(df: pd.DataFrame, path: Path = CLEANED_CSV_PATH) -> None:
    """Persist the cleaned DataFrame to CSV (without the tagged_description column)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.drop(columns=["tagged_description"], errors="ignore")
    out.to_csv(path, index=False)
    logger.info("Saved cleaned CSV: %d rows → %s", len(out), path)


def save_tagged_txt(df: pd.DataFrame, path: Path = TAGGED_TXT_PATH) -> None:
    """Write one tagged description per line to a plain-text file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df["tagged_description"].to_csv(path, sep="\n", index=False, header=False)
    logger.info("Saved tagged descriptions: %d lines → %s", len(df), path)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_pipeline(
    raw_csv_path: Path = RAW_CSV_PATH,
    cleaned_csv_path: Path = CLEANED_CSV_PATH,
    tagged_txt_path: Path = TAGGED_TXT_PATH,
) -> dict:
    """
    Run the full ETL pipeline end-to-end.

    Returns a dict with stats for the API response.
    """
    raw_df = load_raw_csv(raw_csv_path)
    rows_raw = len(raw_df)

    clean_df = clean_dataframe(raw_df)
    tagged_df = add_tagged_description(clean_df)

    save_cleaned_csv(tagged_df, cleaned_csv_path)
    save_tagged_txt(tagged_df, tagged_txt_path)

    return {
        "rows_processed": rows_raw,
        "rows_after_clean": len(tagged_df),
    }

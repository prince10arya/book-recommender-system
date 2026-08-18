"""
shared/config.py
----------------
Central configuration: all paths, environment variables, and tunable constants.
Every service imports from here — no path logic lives anywhere else.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------

# When running inside Docker the data volume is mounted at /app/data.
# When running locally the data lives two levels up from backend/.
_DOCKER_DATA = Path("/app/data")
_LOCAL_DATA = Path(__file__).resolve().parent.parent.parent  # project root

DATA_DIR: Path = _DOCKER_DATA if _DOCKER_DATA.exists() else _LOCAL_DATA

# Raw input CSV (downloaded from Kaggle or placed manually)
RAW_CSV_PATH: Path = DATA_DIR / "books.csv"

# Artifacts produced by the Preprocessing Service
CLEANED_CSV_PATH: Path = DATA_DIR / "books_cleaned.csv"
TAGGED_TXT_PATH: Path = DATA_DIR / "tagged_description.txt"

# ChromaDB persistence directory (produced by Embedding Service)
CHROMA_PATH: Path = DATA_DIR / "chroma_db"

# ---------------------------------------------------------------------------
# API keys & model names
# ---------------------------------------------------------------------------

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2-preview")

# ---------------------------------------------------------------------------
# ETL / embedding tuning
# ---------------------------------------------------------------------------

# Minimum description length (characters) to keep a book
MIN_DESC_LENGTH: int = 25

# ChromaDB batching during ingestion
EMBED_BATCH_SIZE: int = 100

# LangChain text splitter settings (one doc per line)
CHUNK_SIZE: int = 1
CHUNK_OVERLAP: int = 1

# How many extra candidates to fetch from ChromaDB before final top-k filter
SEARCH_MULTIPLIER: int = 5
MAX_SEARCH_K: int = 50

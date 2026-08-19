"""
shared/config.py
----------------
Central configuration: all paths, environment variables, and tunable constants.
Every service imports from here — no path logic lives anywhere else.

Embedding backend: OpenRouter  (https://openrouter.ai/api/v1)
  - Compatible with the OpenAI embeddings API format.
  - Set OPENROUTER_API_KEY in your .env file.
  - Change EMBEDDING_MODEL to any OpenRouter embedding model slug.
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

# OpenRouter API key — used for embeddings via the OpenAI-compatible endpoint.
# Obtain yours at https://openrouter.ai/keys
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# Embedding model slug served by OpenRouter.
# Swap to e.g. "openai/text-embedding-3-large" or "cohere/embed-english-v3.0"
# without touching any other code.
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")

# Shared service token used by auth_service.py in each service.
# Override in production via the SERVICE_TOKEN environment variable.
SERVICE_TOKEN: str = os.getenv("SERVICE_TOKEN", "dev-secret-token")

# When set to "true", the Retrieval Service will also require X-Token.
# Default is "false" so the public frontend can call /recommend freely.
REQUIRE_TOKEN: bool = os.getenv("REQUIRE_TOKEN", "false").lower() == "true"


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

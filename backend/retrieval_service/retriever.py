"""
retrieval_service/retriever.py
-------------------------------
Pure read-only retrieval layer: queries ChromaDB and joins results with
the book metadata CSV.

No ETL, no embedding logic here — only consumption of the artifacts
produced by the Preprocessing and Embedding services.

Embeddings are loaded via OpenRouter's OpenAI-compatible endpoint
(same model slug as used during indexing).
"""

from __future__ import annotations

import logging

import pandas as pd

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from shared.config import (
    CHROMA_PATH,
    CLEANED_CSV_PATH,
    EMBEDDING_MODEL,
    MAX_SEARCH_K,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    SEARCH_MULTIPLIER,
)
from shared.models import BookResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singletons (initialised once at startup via initialize())
# ---------------------------------------------------------------------------

_db: Chroma | None = None
_books_df: pd.DataFrame | None = None


# ---------------------------------------------------------------------------
# Startup initialisation
# ---------------------------------------------------------------------------


def initialize() -> None:
    """
    Load the book metadata DataFrame and ChromaDB into memory.
    Called once during FastAPI lifespan — fails fast if artifacts are missing.
    """
    global _db, _books_df

    if not CLEANED_CSV_PATH.exists():
        raise RuntimeError(
            f"books_cleaned.csv not found at {CLEANED_CSV_PATH}. "
            "Run the Preprocessing Service first."
        )
    if not CHROMA_PATH.exists() or not any(CHROMA_PATH.iterdir()):
        raise RuntimeError(
            f"ChromaDB not found at {CHROMA_PATH}. "
            "Run the Embedding Service first."
        )

    logger.info("Loading books metadata from %s...", CLEANED_CSV_PATH)
    _books_df = pd.read_csv(CLEANED_CSV_PATH)
    _books_df["isbn13"] = _books_df["isbn13"].astype(str)

    logger.info("Loading ChromaDB from %s...", CHROMA_PATH)
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENROUTER_API_KEY,       # type: ignore[arg-type]
        openai_api_base=OPENROUTER_BASE_URL,
    )
    _db = Chroma(
        persist_directory=str(CHROMA_PATH),
        embedding_function=embeddings,
    )
    logger.info("Retriever initialised and ready.")


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


def _safe_str(val, fallback: str = "") -> str:
    """Return empty string for NaN/None, otherwise str."""
    return str(val) if pd.notna(val) else fallback


def retrieve(query: str, top_k: int = 10) -> list[BookResult]:
    """
    Perform a semantic similarity search and return enriched book results.

    Args:
        query:  Natural-language search query.
        top_k:  Number of results to return.

    Returns:
        List of BookResult objects sorted by similarity_score descending.

    Raises:
        RuntimeError: If the retriever has not been initialised.
    """
    if _db is None or _books_df is None:
        raise RuntimeError("Retriever not initialised. Call initialize() first.")

    # Fetch more candidates than needed, then filter after metadata join
    search_k = min(MAX_SEARCH_K, top_k * SEARCH_MULTIPLIER)
    raw_results = _db.similarity_search_with_score(query, k=search_k)

    records = []
    for doc, distance in raw_results:
        isbn = doc.page_content.split()[0].strip("\"' ")
        # ChromaDB returns cosine distance [0, 2]; convert to similarity %
        sim_percent = max(0.0, (1 - (distance / 2)) * 100)
        records.append({"isbn13": isbn, "similarity_score": round(sim_percent, 2)})

    res_df = pd.DataFrame(records)
    if res_df.empty:
        return []

    final_df = pd.merge(res_df, _books_df, on="isbn13")
    final_df = final_df.sort_values(by="similarity_score", ascending=False).head(top_k)

    results: list[BookResult] = []
    for _, row in final_df.iterrows():
        results.append(
            BookResult(
                isbn13=_safe_str(row.get("isbn13")),
                isbn10=_safe_str(row.get("isbn10")),
                title=_safe_str(row.get("title")),
                title_and_subtitle=_safe_str(row.get("title_and_subtitle")) or _safe_str(row.get("title")),
                authors=_safe_str(row.get("authors")),
                categories=_safe_str(row.get("categories")),
                thumbnail=_safe_str(row.get("thumbnail")),
                description=_safe_str(row.get("description")),
                published_year=(
                    int(row["published_year"]) if pd.notna(row.get("published_year")) else None
                ),
                average_rating=(
                    float(row["average_rating"]) if pd.notna(row.get("average_rating")) else None
                ),
                num_pages=(
                    int(row["num_pages"]) if pd.notna(row.get("num_pages")) else None
                ),
                ratings_count=(
                    int(row["ratings_count"]) if pd.notna(row.get("ratings_count")) else None
                ),
                similarity_score=row.get("similarity_score", 0.0),
            )
        )
    return results

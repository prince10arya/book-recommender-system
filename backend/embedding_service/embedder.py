"""
embedding_service/embedder.py
------------------------------
Generates Gemini embeddings for the tagged book descriptions
and populates a persistent ChromaDB vector store.

Extracted and refactored from the original recommender.py::_get_db().
"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from tqdm import tqdm

from shared.config import (
    CHROMA_PATH,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBED_BATCH_SIZE,
    EMBEDDING_MODEL,
    TAGGED_TXT_PATH,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return a configured Gemini embedding function."""
    return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)


def is_db_populated(chroma_path: Path = CHROMA_PATH) -> bool:
    """Return True if a non-empty ChromaDB already exists on disk."""
    return chroma_path.exists() and any(chroma_path.iterdir())


def get_db_stats(chroma_path: Path = CHROMA_PATH) -> dict:
    """
    Return basic ChromaDB stats without embedding any new documents.
    Raises RuntimeError if the DB does not exist.
    """
    if not is_db_populated(chroma_path):
        return {"exists": False, "document_count": None}

    embeddings = get_embeddings()
    db = Chroma(
        persist_directory=str(chroma_path),
        embedding_function=embeddings,
    )
    count = db._collection.count()
    return {"exists": True, "document_count": count}


# ---------------------------------------------------------------------------
# Core builder
# ---------------------------------------------------------------------------


def build_chroma_db(
    txt_path: Path = TAGGED_TXT_PATH,
    chroma_path: Path = CHROMA_PATH,
    batch_size: int = EMBED_BATCH_SIZE,
    force: bool = False,
) -> dict:
    """
    Read `tagged_description.txt`, embed every line with Gemini, and persist
    the result to ChromaDB.

    Args:
        txt_path:    Path to the tagged descriptions text file.
        chroma_path: Directory where ChromaDB will be persisted.
        batch_size:  Number of documents per embedding API call.
        force:       If True, rebuild even if the DB already exists.

    Returns:
        A dict with ``documents_embedded`` count.

    Raises:
        FileNotFoundError: If `txt_path` does not exist.
    """
    if not txt_path.exists():
        raise FileNotFoundError(
            f"Tagged descriptions file not found at {txt_path}. "
            "Run the Preprocessing Service first (POST /preprocess)."
        )

    if is_db_populated(chroma_path) and not force:
        logger.info("ChromaDB already exists and force=False — skipping rebuild.")
        stats = get_db_stats(chroma_path)
        return {"documents_embedded": stats["document_count"], "skipped": True}

    logger.info("Loading tagged descriptions from %s...", txt_path)
    loader = TextLoader(str(txt_path), encoding="utf-8")
    raw_docs = loader.load()

    splitter = CharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separator="\n",
    )
    docs = splitter.split_documents(raw_docs)
    logger.info("Split into %d documents.", len(docs))

    batches = [docs[i : i + batch_size] for i in range(0, len(docs), batch_size)]
    logger.info("Embedding %d documents in %d batches...", len(docs), len(batches))

    embeddings = get_embeddings()
    chroma_path.mkdir(parents=True, exist_ok=True)

    # First batch creates the DB; subsequent batches add to it
    db = Chroma.from_documents(
        documents=batches[0],
        embedding=embeddings,
        persist_directory=str(chroma_path),
    )

    for batch in tqdm(batches[1:], desc="Building ChromaDB", unit="batch"):
        db.add_documents(batch)

    logger.info("ChromaDB built and persisted at %s (%d docs).", chroma_path, len(docs))
    return {"documents_embedded": len(docs), "skipped": False}

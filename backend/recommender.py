import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tqdm import tqdm

load_dotenv()

# Resolve paths relative to the project root (one level up from backend/)
PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH =  PROJECT_ROOT / "books_cleaned.csv"
TXT_PATH =  PROJECT_ROOT / "tagged_description.txt"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

_db: Chroma | None = None
_books_df: pd.DataFrame | None = None


def initialize() -> None:
    """Eagerly build or load ChromaDB at server startup."""
    _load_books()
    _get_db()
    print("Recommender initialized and ready.")


def _load_books() -> pd.DataFrame:
    global _books_df
    if _books_df is None:
        _books_df = pd.read_csv(CSV_PATH)
        _books_df["isbn13"] = _books_df["isbn13"].astype(str)
    return _books_df


def _get_db() -> Chroma:
    """Load or create the ChromaDB vector store."""
    global _db
    if _db is not None:
        return _db

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

    # If we already built the DB, just load it
    if CHROMA_PATH.exists() and any(CHROMA_PATH.iterdir()):
        print("Loading existing ChromaDB from disk...")
        _db = Chroma(
            persist_directory=str(CHROMA_PATH),
            embedding_function=embeddings,
        )
        return _db

    # Build from scratch using the tagged_description.txt
    print("Building ChromaDB from tagged_description.txt (this may take a while)...")
    if not TXT_PATH.exists():
        # Generate the txt file from CSV if it doesn't exist
        books = _load_books()
        books["tagged_description"].to_csv(
            TXT_PATH, sep="\n", index=False, header=False
        )

    loader = TextLoader(str(TXT_PATH), encoding="utf-8")
    raw_docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=1, chunk_overlap=1, separator="\n")
    docs = splitter.split_documents(raw_docs)

    BATCH_SIZE = 100
    batches = [docs[i : i + BATCH_SIZE] for i in range(0, len(docs), BATCH_SIZE)]

    print(f"Embedding {len(docs)} documents in {len(batches)} batches...")

    # Create DB with the first batch, then add the rest
    _db = Chroma.from_documents(
        documents=batches[0],
        embedding=embeddings,
        persist_directory=str(CHROMA_PATH),
    )

    for batch in tqdm(batches[1:], desc="Building ChromaDB", unit="batch"):
        _db.add_documents(batch)

    print("ChromaDB built and persisted.")
    return _db


def retrieve_recommendations(query: str, top_k: int = 10) -> list[dict]:
    """
    Retrieve semantically similar book recommendations for a given query.

    Args:
        query: Natural-language search query.
        top_k: Number of top recommendations to return.

    Returns:
        List of book dicts (sorted by similarity_score desc).
    """
    db = _get_db()
    books = _load_books()

    # Search wider, then take top_k after merging
    raw_results = db.similarity_search_with_score(query, k=min(50, top_k * 5))

    records = []
    for doc, distance in raw_results:
        isbn = doc.page_content.split()[0].strip("\"' ")
        # Cosine distance → similarity %: (1 - d/2) * 100
        sim_percent = max(0.0, (1 - (distance / 2)) * 100)
        records.append({"isbn13": isbn, "similarity_score": round(sim_percent, 2)})

    res_df = pd.DataFrame(records)
    final_df = pd.merge(res_df, books, on="isbn13")
    final_df = final_df.sort_values(by="similarity_score", ascending=False).head(top_k)

    def _str(val, fallback: str = "") -> str:
        """Return empty string for NaN/None, otherwise str."""
        return str(val) if pd.notna(val) else fallback

    # Convert to list of dicts, handling NaN gracefully
    result = []
    for _, row in final_df.iterrows():
        result.append(
            {
                "isbn13": _str(row.get("isbn13")),
                "isbn10": _str(row.get("isbn10")),
                "title": _str(row.get("title")),
                "title_and_subtitle": _str(row.get("title_and_subtitle")) or _str(row.get("title")),
                "authors": _str(row.get("authors")),
                "categories": _str(row.get("categories")),
                "thumbnail": _str(row.get("thumbnail")),
                "description": _str(row.get("description")),
                "published_year": (
                    int(row["published_year"])
                    if pd.notna(row.get("published_year"))
                    else None
                ),
                "average_rating": (
                    float(row["average_rating"])
                    if pd.notna(row.get("average_rating"))
                    else None
                ),
                "num_pages": (
                    int(row["num_pages"]) if pd.notna(row.get("num_pages")) else None
                ),
                "ratings_count": (
                    int(row["ratings_count"])
                    if pd.notna(row.get("ratings_count"))
                    else None
                ),
                "similarity_score": row.get("similarity_score", 0.0),
            }
        )
    return result

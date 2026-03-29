from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from recommender import retrieve_recommendations, initialize


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build/load ChromaDB once before accepting requests."""
    print("Starting up — initializing ChromaDB...")
    initialize()
    yield
    print("Shutting down.")

app = FastAPI(
    title="Book Recommender API",
    description="Semantic book recommendations powered by ChromaDB + Google Generative AI Embeddings",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results")


class BookResult(BaseModel):
    isbn13: str
    isbn10: str
    title: str
    title_and_subtitle: str
    authors: str
    categories: str
    thumbnail: str
    description: str
    published_year: int | None
    average_rating: float | None
    num_pages: int | None
    ratings_count: int | None
    similarity_score: float


class RecommendResponse(BaseModel):
    query: str
    results: list[BookResult]
    total: int


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Book Recommender API is running"}


@app.post("/recommend", response_model=RecommendResponse, tags=["Recommendations"])
async def recommend_books(request: RecommendRequest):
    """
    Get semantically similar book recommendations for a natural-language query.
    """
    try:
        results = retrieve_recommendations(request.query, request.top_k)
        return RecommendResponse(
            query=request.query,
            results=results,
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

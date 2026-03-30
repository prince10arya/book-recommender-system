# Book Recommender System

A full-stack semantic book recommendation engine powered by Google Generative AI Embeddings, ChromaDB, FastAPI, and Next.js.

## What We Have Done

We have built a two-part application to provide highly accurate, semantic book recommendations based on natural language queries:

1. **Backend (Python / FastAPI)**:
   - Built a REST API featuring a `/recommend` endpoint.
   - Integrated **ChromaDB** as our local vector database, handling high-performance similarity searches.
   - Utilized **Google Generative AI Embeddings** (`gemini-embedding-2-preview`) to convert book descriptions into high-dimensional vector embeddings, allowing the system to understand the context and meaning of the books.
   - Created an automated ETL pipeline that processes a cleaned dataset (`books_cleaned.csv`), extracts tagged descriptions, chunks the text, and persists it into ChromaDB on startup.

2. **Frontend (Next.js / React)**:
   - Built a sleek, responsive user interface using Next.js 16 and React 19.
   - Implemented a search bar and a results grid (`SkeletonGrid`, `BookCard`, `BookModal`) to seamlessly capture user queries and display the recommended books along with their metadata (e.g., summary, cover image, rating, similarity score).

## Why We Did It

- **Semantic Understanding vs. Keyword Matching**: Traditional search engines rely heavily on exact keyword matches. By utilizing vector embeddings, our system understands the *meaning* behind a user's query. For example, searching for "a story about a wizard in a magical school" will recommend Harry Potter, even if those exact words aren't in the book's title.
- **Speed and Efficiency**: By leveraging ChromaDB locally, we ensure that similarity search lookups (computing cosine distances) happen in milliseconds.
- **Modern User Experience**: We chose Next.js to provide a fast, modern frontend that easily communicates with our FastAPI backend, providing an instantaneous feedback loop for the user.

## Running the Project

### Prerequisites
- Python 3.10+
- Node.js & npm (or yarn/pnpm)
- A Google Gemini API Key added to your `.env` file (`GOOGLE_API_KEY=your-api-key`)

### Backend Setup
1. Navigate to the `backend/` directory.
2. Install dependencies (e.g., using `pip` or `uv`).
3. Place `books_cleaned.csv` in the root directory.
4. Run the FastAPI server:
   ```bash
   fastapi dev main.py
   ```
   *(On first run, this will build the ChromaDB from scratch which may take some time.)*

### Frontend Setup
1. Navigate to the `frontend/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

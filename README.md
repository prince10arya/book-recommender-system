<div align="center">
  <h1>📚 Book Recommender System 🔍</h1>
  <p><i>A full-stack, semantic book recommendation engine powered by GenAI & vector search</i></p>

  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" /></a>
  <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" /></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" /></a>
  <a href="https://www.trychroma.com/"><img src="https://img.shields.io/badge/ChromaDB-FF6600?style=for-the-badge" alt="ChromaDB" /></a>
  <a href="https://ai.google.dev/"><img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini Embeddings" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" /></a>
</div>

<br/>

## ✨ Overview

This project is a powerful, two-part application designed to provide highly accurate and contextual book recommendations using natural language queries instead of traditional keyword matching.

### 🧠 How It Works (What We Have Done)

* **Backend (Python / FastAPI)** 🚀
  * Features a hyper-fast REST API with a dedicated `/recommend` endpoint.
  * Uses **Google Generative AI Embeddings** (`gemini-embedding-2-preview`) to convert book descriptions into high-dimensional vector embeddings, allowing the system to truly understand context and plot arcs.
  * Integrated **ChromaDB** as the local vector database for blazing-fast similarity searches.
  * Incorporates an automated ETL pipeline that processes `books_cleaned.csv`, extracting and chunking tagged descriptions directly into ChromaDB on startup.

* **Frontend (Next.js / React)** 💻
  * A sleek, responsive user interface built using the bleeding-edge Next.js 16 and React 19.
  * Seamlessly handles user interactions via a custom search bar and displays dynamic results using custom components (`SkeletonGrid`, `BookCard`, `BookModal`).
  * Instantaneously surfaces rich book metadata alongside context-aware similarity scores.

## 💡 Why We Built It

- **Semantic Understanding over Keywords** 🎯
  Traditional search struggles unless you type the exact title. Our vector-based engine understands *meaning*. If you search for *"a story about a boy going to a wizarding school"*, it will recommend *Harry Potter*, even if the search terms are missing from the book!
- **Blazing Fast Performance** ⚡
  By utilizing a local instance of ChromaDB, calculating complex cosine distances between multidimensional vectors happens in mere milliseconds.
- **Modern User Experience** 🎨
  Next.js provides an incredibly fast, dynamic frontend. Paired with our backend, it constructs an instantaneous feedback loop for users seamlessly traversing the literary world.

---

## 🛠 Tech Stack

| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind | The modern web framework driving the user interface |
| **Backend API** | FastAPI, Python 3.10+ | High-performance async server |
| **Vector DB** | ChromaDB | Specialized database tailored for embedding storage & retrieval |
| **AI / Embeddings** | Google Gemini `gemini-embedding-2-preview` | The brain behind our semantic text comprehension |
| **Data Processing** | Pandas, LangChain Text Splitters | Cleans, structures, and chunks data for embeddings |

---

## 🚀 Running the Project

### 📋 Prerequisites
- Python 3.10+
- Node.js & npm (or yarn/pnpm)
- A Google Gemini API Key added to your backend `.env` file:
  ```env
  GOOGLE_API_KEY=your-api-key
  ```

### ⚙️ Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install dependencies (e.g., using `pip` or `uv`):
   ```bash
   pip install -r requirements.txt
   ```
3. Place your raw dataset `books_cleaned.csv` into the root directory.
4. Launch the FastAPI server:
   ```bash
   fastapi dev main.py
   ```
   *Note: On your very first run, the system will process the dataset and build the ChromaDB from scratch. This may take a few moments.*

### 🖥️ Frontend Setup
1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Access the application at: [http://localhost:3000](http://localhost:3000)

<br/>
<div align="center">
  <i>Happy Reading!</i>
</div>


<div>
  <h1>🎥 Project Demo</h1>
  <p align="center">
    <a href="https://www.youtube.com/watch?v=_ZM0_wCjI9wD">
      <img src="https://i9.ytimg.com/vi_webp/_ZM0_wCjI9w/mq3.webp?sqp=CKjVuc4G-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYACzgWKAgwIABABGHIgWigtMA8=&rs=AOn4CLDMgdkRoozLDrkkXENkSrxVLZUHeQ" alt="Watch Demo">
    </a>
  </p>
</div>

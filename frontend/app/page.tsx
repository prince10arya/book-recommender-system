'use client';

import { useState, useCallback } from 'react';
import SearchBar from './components/SearchBar';
import BookCard from './components/BookCard';
import BookModal from './components/BookModal';
import SkeletonGrid from './components/SkeletonGrid';
import { Book, RecommendResponse } from './types';

type UIState = 'idle' | 'loading' | 'results' | 'error';

export default function HomePage() {
  const [uiState, setUiState] = useState<UIState>('idle');
  const [books, setBooks] = useState<Book[]>([]);
  const [lastQuery, setLastQuery] = useState('');
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSearch = useCallback(async (query: string) => {
    setUiState('loading');
    setLastQuery(query);
    setBooks([]);
    setErrorMsg('');

    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 12 }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error ?? 'Request failed');
      }

      const data: RecommendResponse = await res.json();
      setBooks(data.results);
      setUiState('results');
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Something went wrong');
      setUiState('error');
    }
  }, []);

  return (
    <>
      {/* Navbar */}
      <nav className="nav">
        <a href="/" className="nav-logo">
          <span className="nav-logo-dot" />
          BookMind
        </a>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Powered by Semantic AI
        </span>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">
          <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z" />
          </svg>
          Vector-powered recommendations
        </div>

        <h1 className="hero-title">
          Find your next <span>great read</span>
        </h1>
        <p className="hero-subtitle">
          Describe the book you&apos;re looking for in plain English — our AI finds the best matches from 6,000+ books.
        </p>

        <SearchBar onSearch={handleSearch} loading={uiState === 'loading'} />

        {uiState === 'results' && (
          <p className="result-count" style={{ marginTop: 20 }}>
            Showing <strong>{books.length}</strong> recommendations for &ldquo;<strong>{lastQuery}</strong>&rdquo;
          </p>
        )}
      </section>

      {/* States */}
      {uiState === 'loading' && <SkeletonGrid count={12} />}

      {uiState === 'error' && (
        <div style={{ padding: '0 24px' }}>
          <div className="error-banner">
            ⚠️ {errorMsg}
            <br />
            <small>Make sure the backend is running on port 8000.</small>
          </div>
        </div>
      )}

      {uiState === 'results' && books.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">📚</div>
          <h3>No matches found</h3>
          <p>Try a different description or broader search terms.</p>
        </div>
      )}

      {uiState === 'results' && books.length > 0 && (
        <div className="books-grid">
          {books.map((book, i) => (
            <BookCard
              key={book.isbn13}
              book={book}
              delay={i * 50}
              onClick={() => setSelectedBook(book)}
            />
          ))}
        </div>
      )}

      {uiState === 'idle' && (
        <div className="empty-state" style={{ paddingTop: 40 }}>
          <div className="empty-state-icon">🔍</div>
          <h3>Start searching</h3>
          <p>Type any description or mood and let the AI find the perfect books for you.</p>

          {/* Sample prompts */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, justifyContent: 'center', marginTop: 24 }}>
            {[
              'a book about nature and wonder',
              'mystery thriller in a small town',
              'sci-fi with psychological depth',
              'philosophy for beginners',
            ].map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleSearch(prompt)}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: '50px',
                  padding: '8px 18px',
                  fontSize: '0.82rem',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'border-color 0.2s, color 0.2s',
                  fontFamily: 'inherit',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-hover)';
                  e.currentTarget.style.color = 'var(--accent)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Modal */}
      {selectedBook && (
        <BookModal book={selectedBook} onClose={() => setSelectedBook(null)} />
      )}

      {/* Footer */}
      <footer className="footer">
        <p>BookMind &mdash; Semantic book recommendations using ChromaDB &amp; Google Generative AI</p>
      </footer>
    </>
  );
}

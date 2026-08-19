'use client';

import { useState, useCallback, useRef } from 'react';
import BookCard from './components/BookCard';
import BookModal from './components/BookModal';
import SkeletonGrid from './components/SkeletonGrid';
import { Book, RecommendResponse } from './types';

type UIState = 'idle' | 'loading' | 'results' | 'error';

const SAMPLE_PROMPTS = [
  'a boy at a wizarding school',
  'mystery thriller in a small town',
  'sci-fi with psychological depth',
  'philosophy for beginners',
  'epic fantasy adventure',
  'self-help productivity',
];

const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

export default function HomePage() {
  const [uiState, setUiState] = useState<UIState>('idle');
  const [books, setBooks] = useState<Book[]>([]);
  const [lastQuery, setLastQuery] = useState('');
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Separate refs for hero and nav search inputs
  const heroInputRef = useRef<HTMLInputElement>(null);
  const navInputRef = useRef<HTMLInputElement>(null);

  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setUiState('loading');
    setLastQuery(query.trim());
    setBooks([]);
    setErrorMsg('');

    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), top_k: 20 }),
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

  const handleHeroSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (heroInputRef.current) handleSearch(heroInputRef.current.value);
  };

  const handleNavSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (navInputRef.current) handleSearch(navInputRef.current.value);
  };

  const isLoading = uiState === 'loading';

  return (
    <>
      {/* ── Primary Nav ── */}
      <nav className="nav">
        {/* Logo */}
        <a href="/" className="nav-logo">
          <span className="nav-logo-icon">B</span>
          <span className="nav-wordmark">BookMind</span>
        </a>
      </nav>

      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-eyebrow">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z" /></svg>
          Semantic AI recommendations
        </div>

        <h1 className="hero-title">
          Discover books you&apos;ll{' '}
          <span className="hero-title-accent">love</span>
        </h1>

        <p className="hero-subtitle">
          Describe what you&apos;re in the mood for in plain English. Our AI finds the perfect books from 6,000+ titles.
        </p>

        {/* Hero search bar */}
        <div className="hero-search-wrap">
          <form className="hero-search" onSubmit={handleHeroSubmit}>
            <span className="hero-search-icon"><SearchIcon /></span>
            <input
              ref={heroInputRef}
              id="hero-search-input"
              className="hero-search-input"
              type="search"
              placeholder="a story about a boy going to a wizarding school..."
              aria-label="Describe the book you're looking for"
            />
            <button
              id="hero-search-btn"
              type="submit"
              className="btn-primary"
              disabled={isLoading}
            >
              {isLoading ? (
                <svg className="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10" strokeOpacity="0.3" /><path d="M12 2a10 10 0 0 1 10 10" /></svg>
              ) : (
                <>Search</>
              )}
            </button>
          </form>

          {/* Sample prompts */}
          {uiState === 'idle' && (
            <div className="sample-chips" role="list" aria-label="Sample searches">
              {SAMPLE_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  role="listitem"
                  className="sample-chip"
                  onClick={() => {
                    if (heroInputRef.current) heroInputRef.current.value = prompt;
                    handleSearch(prompt);
                  }}
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── Loading ── */}
      {isLoading && <SkeletonGrid count={20} />}

      {/* ── Error ── */}
      {uiState === 'error' && (
        <div style={{ padding: '0 24px' }}>
          <div className="error-banner" role="alert">
            ⚠️ {errorMsg}
            <br />
            <small>Make sure the backend is running on port 8000.</small>
          </div>
        </div>
      )}

      {/* ── No results ── */}
      {uiState === 'results' && books.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">📚</div>
          <h3>No matches found</h3>
          <p>Try a different description or broader search terms.</p>
        </div>
      )}

      {/* ── Results ── */}
      {uiState === 'results' && books.length > 0 && (
        <>
          <div className="results-header">
            <p className="results-label">
              <strong>{books.length}</strong> recommendations for &ldquo;<strong>{lastQuery}</strong>&rdquo;
            </p>
          </div>

          <div className="pin-grid" role="list" aria-label="Book recommendations">
            {books.map((book, i) => (
              <BookCard
                key={book.isbn13}
                book={book}
                delay={i * 40}
                onClick={() => setSelectedBook(book)}
              />
            ))}
          </div>
        </>
      )}

      {/* ── Idle state ── */}
      {uiState === 'idle' && (
        <div className="empty-state" style={{ paddingTop: 0 }}>
          <div className="empty-state-icon">📖</div>
          <h3>What are you in the mood for?</h3>
          <p>Try a prompt above or type your own description.</p>
        </div>
      )}

      {/* ── Book modal ── */}
      {selectedBook && (
        <BookModal book={selectedBook} onClose={() => setSelectedBook(null)} />
      )}

      {/* ── Footer ── */}
      <footer className="footer">
        <a href="/" className="footer-brand">
          <span className="footer-logo">B</span>
          <span className="footer-name">BookMind</span>
        </a>
        <span className="footer-copy">© 2026 BookMind — Semantic book recommendations</span>
        <nav className="footer-links" aria-label="Footer links">
          <a href="#" className="footer-link">About</a>
          <a href="#" className="footer-link">Privacy</a>
          <a href="#" className="footer-link">Help</a>
        </nav>
      </footer>
    </>
  );
}

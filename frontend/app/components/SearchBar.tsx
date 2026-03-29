'use client';

import { useState, KeyboardEvent } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [value, setValue] = useState('');

  const handleSearch = () => {
    const q = value.trim();
    if (q) onSearch(q);
  };

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <div className="search-wrapper">
      <div className="search-bar">
        {/* Search icon */}
        <svg className="search-icon" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>

        <input
          className="search-input"
          type="text"
          placeholder='Try "a mystery thriller set in Japan" or "books about AI"…'
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading}
          aria-label="Book search query"
          id="book-search-input"
        />

        <button
          className="search-btn"
          onClick={handleSearch}
          disabled={loading || !value.trim()}
          id="search-button"
          aria-label="Search for books"
        >
          {loading ? (
            <>
              <svg className="spin" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M21 12a9 9 0 1 1-9-9" strokeLinecap="round" />
              </svg>
              Searching…
            </>
          ) : (
            <>
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path d="m5 12 14 0M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Find Books
            </>
          )}
        </button>
      </div>
    </div>
  );
}

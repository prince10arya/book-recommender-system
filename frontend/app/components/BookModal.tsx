'use client';

import { useEffect } from 'react';
import Image from 'next/image';
import { Book } from '../types';

interface Props {
  book: Book;
  onClose: () => void;
}

export default function BookModal({ book, onClose }: Props) {
  // Close on Escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  // Lock body scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  const hasCover = !!book.thumbnail;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label={`Book details: ${book.title}`}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="modal">
        <div className="modal-inner">
          {/* Left: full-bleed cover */}
          <div className="modal-cover-col">
            {hasCover ? (
              <Image
                src={book.thumbnail}
                alt={`Cover of ${book.title}`}
                fill
                sizes="220px"
                style={{ objectFit: 'cover' }}
                unoptimized
              />
            ) : (
              <div className="modal-cover-fallback">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#c8c8c1" strokeWidth="1.5">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                </svg>
                <div className="modal-cover-fallback-title">{book.title}</div>
              </div>
            )}
            {/* Similarity pill overlay */}
            <div className="modal-sim-pill" aria-label={`${book.similarity_score}% match`}>
              {book.similarity_score.toFixed(1)}% match
            </div>
          </div>

          {/* Right: content */}
          <div className="modal-content">
            {/* Close button */}
            <button
              id="modal-close-btn"
              className="modal-close"
              onClick={onClose}
              aria-label="Close modal"
            >
              ✕
            </button>

            {/* Title & author */}
            <div>
              <h2 className="modal-title">{book.title_and_subtitle || book.title}</h2>
              <p className="modal-author">by {book.authors}</p>
            </div>

            {/* Chips */}
            <div className="modal-chips">
              {book.categories && (
                <span className="chip chip-category">{book.categories}</span>
              )}
              {book.published_year && (
                <span className="chip chip-year">{book.published_year}</span>
              )}
            </div>

            <div className="modal-divider" />

            {/* Stats */}
            <div className="modal-stats">
              {book.average_rating != null && (
                <div className="stat">
                  <span className="stat-value" style={{ color: '#e60023' }}>
                    {'★'.repeat(Math.round(book.average_rating))}{'☆'.repeat(5 - Math.round(book.average_rating))}
                  </span>
                  <span className="stat-label">{book.average_rating.toFixed(2)} rating</span>
                </div>
              )}
              {book.num_pages != null && (
                <div className="stat">
                  <span className="stat-value">{book.num_pages.toLocaleString()}</span>
                  <span className="stat-label">Pages</span>
                </div>
              )}
              {book.ratings_count != null && (
                <div className="stat">
                  <span className="stat-value">{book.ratings_count.toLocaleString()}</span>
                  <span className="stat-label">Ratings</span>
                </div>
              )}
            </div>

            {/* Description */}
            {book.description && (
              <>
                <div className="modal-divider" />
                <p className="modal-description">{book.description}</p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

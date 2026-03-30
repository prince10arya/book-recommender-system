'use client';

import Image from 'next/image';
import { useState } from 'react';
import { Book } from '../types';

interface BookModalProps {
  book: Book;
  onClose: () => void;
}

export default function BookModal({ book, onClose }: BookModalProps) {
  const [imgError, setImgError] = useState(false);
  const hasImage = book.thumbnail && !imgError;

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} role="dialog" aria-modal aria-label={book.title}>
      <div className="modal">
        <div className="modal-inner">
          {/* Cover */}
          <div className="modal-cover-col">
            {hasImage ? (
              <Image
                src={book.thumbnail}
                alt={book.title}
                fill
                style={{ objectFit: 'cover' }}
                unoptimized
                onError={() => setImgError(true)}
              />
            ) : (
              <div className="modal-cover-fallback">
                <svg width="48" height="48" fill="none" stroke="currentColor" strokeWidth="1" viewBox="0 0 24 24">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            )}
            <div className="modal-badge">{book.similarity_score.toFixed(0)}% match</div>
          </div>

          {/* Content */}
          <div className="modal-content">
            <button id="modal-close-btn" className="modal-close" onClick={onClose} aria-label="Close modal">
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M18 6 6 18M6 6l12 12" strokeLinecap="round" />
              </svg>
            </button>

            <h2 className="modal-title">{book.title_and_subtitle || book.title}</h2>
            <p className="modal-author">by {book.authors}</p>

            <div className="modal-chips">
              {book.categories && <span className="chip chip-category">{book.categories}</span>}
              {book.published_year && <span className="chip chip-year">{book.published_year}</span>}
            </div>

            <div className="modal-divider" />

            <div className="modal-stats">
              {book.average_rating != null && (
                <div className="stat">
                  <div className="stat-value" style={{ color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z" />
                    </svg>
                    {book.average_rating.toFixed(1)}
                  </div>
                  <div className="stat-label">Rating</div>
                </div>
              )}
              {book.ratings_count != null && (
                <div className="stat">
                  <div className="stat-value">{book.ratings_count.toLocaleString()}</div>
                  <div className="stat-label">Reviews</div>
                </div>
              )}
              {book.num_pages != null && (
                <div className="stat">
                  <div className="stat-value">{book.num_pages}</div>
                  <div className="stat-label">Pages</div>
                </div>
              )}
            </div>

            {book.description && (
              <>
                <div className="modal-divider" />
                <p className="modal-description">{book.description}</p>
              </>
            )}

            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
              ISBN: {book.isbn13}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

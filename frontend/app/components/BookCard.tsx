'use client';

import Image from 'next/image';
import { useState } from 'react';
import { Book } from '../types';

interface BookCardProps {
  book: Book;
  onClick: () => void;
  delay?: number;
}

export default function BookCard({ book, onClick, delay = 0 }: BookCardProps) {
  const [imgError, setImgError] = useState(false);
  const hasImage = book.thumbnail && !imgError;

  return (
    <article
      className="book-card"
      onClick={onClick}
      style={{ animationDelay: `${delay}ms` }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      aria-label={`${book.title} by ${book.authors}`}
    >
      <div className="book-cover-wrapper">
        {hasImage ? (
          <Image
            className="book-cover"
            src={book.thumbnail}
            alt={book.title}
            fill
            sizes="(max-width: 640px) 160px, 200px"
            onError={() => setImgError(true)}
            unoptimized
          />
        ) : (
          <div className="book-cover-fallback">
            <svg width="36" height="36" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span>{book.title_and_subtitle || book.title}</span>
          </div>
        )}
        <div className="similarity-badge">{book.similarity_score.toFixed(0)}% match</div>
      </div>

      <div className="book-info">
        <h3 className="book-title">{book.title_and_subtitle || book.title}</h3>
        <p className="book-author">{book.authors}</p>
        <div className="book-meta">
          {book.average_rating ? (
            <div className="book-rating">
              <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z" />
              </svg>
              {book.average_rating.toFixed(1)}
            </div>
          ) : null}
          {book.categories && (
            <div className="category-chip">{book.categories}</div>
          )}
        </div>
      </div>
    </article>
  );
}

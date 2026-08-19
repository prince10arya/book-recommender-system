'use client';

import Image from 'next/image';
import { Book } from '../types';

interface Props {
  book: Book;
  delay?: number;
  onClick: () => void;
}

export default function BookCard({ book, delay = 0, onClick }: Props) {
  const hasCover = !!book.thumbnail;
  const ratingStars = book.average_rating
    ? '★'.repeat(Math.round(book.average_rating)) + '☆'.repeat(5 - Math.round(book.average_rating))
    : null;

  return (
    <article
      className="pin-card"
      role="listitem"
      style={{ animationDelay: `${delay}ms` }}
      onClick={onClick}
      tabIndex={0}
      aria-label={`${book.title} by ${book.authors}`}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {/* Cover — full bleed, no padding */}
      <div className="pin-cover-wrap">
        {hasCover ? (
          <Image
            src={book.thumbnail}
            alt={`Cover of ${book.title}`}
            fill
            sizes="(max-width: 480px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, 20vw"
            className="pin-cover"
            unoptimized
          />
        ) : (
          <div className="pin-cover-fallback">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#91918c" strokeWidth="1.5">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
            <div className="pin-cover-fallback-title">{book.title}</div>
            <div className="pin-cover-fallback-author">{book.authors}</div>
          </div>
        )}

        {/* Similarity pill — overlay on cover */}
        <span className="pin-sim-pill" aria-label={`${book.similarity_score}% match`}>
          {book.similarity_score.toFixed(0)}% match
        </span>

        {/* Save pill on hover */}
        <button className="pin-save-pill" aria-label="View book details" onClick={(e) => { e.stopPropagation(); onClick(); }}>
          View
        </button>
      </div>

      {/* Metadata below image */}
      <div className="pin-meta">
        <p className="pin-title">{book.title_and_subtitle || book.title}</p>
        <p className="pin-author">{book.authors}</p>
        {ratingStars && (
          <div className="pin-rating" aria-label={`Rating: ${book.average_rating} out of 5`}>
            <span style={{ color: '#e60023', fontSize: '11px', letterSpacing: '-1px' }}>{ratingStars}</span>
            <span>{book.average_rating?.toFixed(1)}</span>
          </div>
        )}
      </div>
    </article>
  );
}

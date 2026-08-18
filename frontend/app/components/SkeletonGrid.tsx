'use client';

// Varying aspect ratios to mimic real masonry pin heights
const ASPECTS = ['2/3', '3/4', '4/5', '1/1', '2/3', '3/4'];

export default function SkeletonGrid({ count = 20 }: { count?: number }) {
  return (
    <div className="skeleton-pin-grid" aria-label="Loading books..." aria-busy="true">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-pin">
          <div
            className="skeleton-cover"
            style={{ aspectRatio: ASPECTS[i % ASPECTS.length] }}
          />
          <div className="skeleton-meta">
            <div className="skeleton-line" />
            <div className="skeleton-line short" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function SkeletonGrid({ count = 10 }: { count?: number }) {
  return (
    <div className="skeleton-grid">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-card" style={{ animationDelay: `${i * 40}ms` }}>
          <div className="skeleton-cover" />
          <div className="skeleton-info">
            <div className="skeleton-line" style={{ width: '90%' }} />
            <div className="skeleton-line" style={{ width: '65%' }} />
            <div className="skeleton-line" style={{ width: '45%', marginTop: 4 }} />
          </div>
        </div>
      ))}
    </div>
  );
}

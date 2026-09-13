export default function LoadingState({ count = 8 }) {
  return (
    <div className="loading-grid" aria-label="Loading photos">
      {Array.from({ length: count }).map((_, index) => (
        <div className="photo-skeleton" key={index}>
          <div className="skeleton-image" />
          <div className="skeleton-line skeleton-title" />
          <div className="skeleton-line skeleton-meta" />
        </div>
      ))}
    </div>
  );
}
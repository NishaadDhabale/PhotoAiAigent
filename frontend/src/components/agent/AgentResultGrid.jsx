import { motion } from "framer-motion";
import { getPhotoImageUrl } from "../../api/photoApi";

function ResultCard({ photo, onClick }) {
  return (
    <motion.button
      type="button"
      className="agent-result-card"
      onClick={() => onClick(photo)}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.98 }}
    >
      <img
        src={getPhotoImageUrl(photo.id)}
        alt={photo.filename}
        className="agent-result-image"
        loading="lazy"
      />

      <div className="agent-result-info">
        <strong>{photo.filename}</strong>

        {photo.date_taken && (
          <span>{photo.date_taken}</span>
        )}

        {photo.location_name && (
          <span>{photo.location_name}</span>
        )}
      </div>
    </motion.button>
  );
}

export default function AgentResultGrid({
  results,
  onPhotoClick,
}) {
  if (!results?.length) {
    return null;
  }

  return (
    <motion.div
      className="agent-results"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <div className="agent-results-heading">
        <span>
          {results.length} photo
          {results.length === 1 ? "" : "s"}
        </span>
      </div>

      <div className="agent-results-grid">
        {results.map((photo) => (
          <ResultCard
            key={photo.id}
            photo={photo}
            onClick={onPhotoClick}
          />
        ))}
      </div>
    </motion.div>
  );
}
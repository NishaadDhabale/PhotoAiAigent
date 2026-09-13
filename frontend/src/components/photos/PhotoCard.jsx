import { motion } from "framer-motion";
import { CalendarDays, Camera } from "lucide-react";

function formatDate(date) {
  if (!date) return null;

  const parsed = new Date(date);

  if (Number.isNaN(parsed.getTime())) {
    return date;
  }

  return parsed.toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function PhotoCard({
  photo,
  imageUrl,
  index = 0,
  onClick,
}) {
  return (
    <motion.button
      type="button"
      className="photo-card"
      onClick={onClick}
      layout
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.3,
        delay: Math.min(index * 0.025, 0.3),
      }}
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.985 }}
    >
      <div className="photo-card-image-wrap">
        <img
          src={imageUrl}
          alt={photo.filename}
          className="photo-card-image"
          loading="lazy"
        />

        <div className="photo-card-overlay">
          <span>View photo</span>
        </div>
      </div>

      <div className="photo-card-info">
        <p className="photo-card-name" title={photo.filename}>
          {photo.filename}
        </p>

        <div className="photo-card-meta">
          {photo.date_taken && (
            <span>
              <CalendarDays size={13} />
              {formatDate(photo.date_taken)}
            </span>
          )}

          {photo.camera && (
            <span title={photo.camera}>
              <Camera size={13} />
              {photo.camera}
            </span>
          )}
        </div>
      </div>
    </motion.button>
  );
}
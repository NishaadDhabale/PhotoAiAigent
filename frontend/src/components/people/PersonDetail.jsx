import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  CalendarDays,
  Camera,
  MapPin,
} from "lucide-react";

import {
  getPersonPhotos,
  getPersonThumbnailUrl,
  getPhotoImageUrl,
} from "../../api/photoApi";

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

export default function PersonDetail({
  person,
  onBack,
  onPhotoClick,
  onPhotosLoaded,
}) {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        setError(null);

        const data = await getPersonPhotos(
          person.group_id
        );

        if (!cancelled) {
          setPhotos(data.results || []);
          const loadedPhotos = data.results || [];

          setPhotos(loadedPhotos);
          onPhotosLoaded?.(loadedPhotos);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "Unable to load person photos."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [person.group_id]);

  return (
    <motion.div
      className="person-detail"
      initial={{ opacity: 0, x: 15 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <button
        type="button"
        className="back-button"
        onClick={onBack}
      >
        <ArrowLeft size={17} />
        All people
      </button>

      <div className="person-detail-header">
        <div className="person-detail-avatar">
          <img
            src={getPersonThumbnailUrl(person.group_id)}
            alt={person.name}
          />
        </div>

        <div>
          <span className="section-label">
            PERSON
          </span>

          <h1>{person.name}</h1>

          <p>
            {person.photo_count}{" "}
            {person.photo_count === 1
              ? "photo"
              : "photos"}{" "}
            · {person.face_count}{" "}
            {person.face_count === 1
              ? "appearance"
              : "appearances"}
          </p>
        </div>
      </div>

      {loading && (
        <div className="people-detail-loading">
          Loading photos...
        </div>
      )}

      {error && (
        <div className="people-detail-error">
          {error}
        </div>
      )}

      {!loading && !error && photos.length === 0 && (
        <div className="empty-state">
          <h2>No photos found</h2>
        </div>
      )}

      {!loading && !error && photos.length > 0 && (
        <div className="person-photo-grid">
          {photos.map((photo, index) => (
            <motion.button
              type="button"
              key={photo.id}
              className="person-photo-card"
              onClick={() => onPhotoClick(photo)}
              initial={{
                opacity: 0,
                y: 12,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              transition={{
                delay: Math.min(index * 0.04, 0.3),
              }}
              whileHover={{
                y: -3,
              }}
            >
              <div className="person-photo-image-wrap">
                <img
                  src={getPhotoImageUrl(photo.id)}
                  alt={photo.filename}
                  loading="lazy"
                />
              </div>

              <div className="person-photo-info">
                <strong>{photo.filename}</strong>

                <div>
                  {photo.date_taken && (
                    <span>
                      <CalendarDays size={12} />
                      {formatDate(photo.date_taken)}
                    </span>
                  )}

                  {photo.camera && (
                    <span>
                      <Camera size={12} />
                      {photo.camera}
                    </span>
                  )}

                  {photo.location_name && (
                    <span>
                      <MapPin size={12} />
                      {photo.location_name}
                    </span>
                  )}
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      )}
    </motion.div>
  );
}
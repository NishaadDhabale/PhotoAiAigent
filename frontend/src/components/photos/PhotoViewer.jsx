import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  CalendarDays,
  Camera,
  ChevronLeft,
  ChevronRight,
  Download,
  MapPin,
  X,
} from "lucide-react";
import { getPhotoImageUrl } from "../../api/photoApi";

function formatDate(date) {
  if (!date) return "Unknown date";

  const parsed = new Date(date);

  if (Number.isNaN(parsed.getTime())) {
    return date;
  }

  return parsed.toLocaleDateString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export default function PhotoViewer({
  photos,
  selectedPhoto,
  onClose,
  onNext,
  onPrevious,
}) {
  useEffect(() => {
    if (!selectedPhoto) return;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      }

      if (event.key === "ArrowRight") {
        onNext();
      }

      if (event.key === "ArrowLeft") {
        onPrevious();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [selectedPhoto, onClose, onNext, onPrevious]);

  return (
    <AnimatePresence>
      {selectedPhoto && (
        <motion.div
          className="photo-viewer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="photo-viewer-content"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            transition={{ duration: 0.2 }}
            onClick={(event) => event.stopPropagation()}
          >
            <button
              type="button"
              className="viewer-close"
              onClick={onClose}
              aria-label="Close viewer"
            >
              <X size={22} />
            </button>

            <button
              type="button"
              className="viewer-nav viewer-prev"
              onClick={onPrevious}
              aria-label="Previous photo"
              disabled={photos.length <= 1}
            >
              <ChevronLeft size={28} />
            </button>

            <div className="viewer-image-container">
              <img
                src={getPhotoImageUrl(selectedPhoto.id)}
                alt={selectedPhoto.filename}
                className="viewer-image"
              />
            </div>

            <button
              type="button"
              className="viewer-nav viewer-next"
              onClick={onNext}
              aria-label="Next photo"
              disabled={photos.length <= 1}
            >
              <ChevronRight size={28} />
            </button>

            <div className="viewer-info">
              <div className="viewer-title-row">
                <div>
                  <h2>{selectedPhoto.filename}</h2>
                  <p>Photo #{selectedPhoto.id}</p>
                </div>

                <a
                  className="viewer-download"
                  href={getPhotoImageUrl(selectedPhoto.id)}
                  download={selectedPhoto.filename}
                  target="_blank"
                  rel="noreferrer"
                  title="Open original image"
                >
                  <Download size={17} />
                  <span>Open original</span>
                </a>
              </div>

              <div className="viewer-metadata">
                <span>
                  <CalendarDays size={15} />
                  {formatDate(selectedPhoto.date_taken)}
                </span>

                {selectedPhoto.camera && (
                  <span>
                    <Camera size={15} />
                    {selectedPhoto.camera}
                  </span>
                )}

                {selectedPhoto.location_name && (
                  <span>
                    <MapPin size={15} />
                    {selectedPhoto.location_name}
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
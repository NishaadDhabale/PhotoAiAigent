import { useEffect } from "react";
import {
  ChevronLeft,
  ChevronRight,
  X,
  FolderOpen,
} from "lucide-react";

import { getPhotoImageUrl, openPhotoLocation } from "../../api/photoApi";

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

  if (!selectedPhoto) {
    return null;
  }

  const currentIndex = photos.findIndex(
    (photo) => photo.id === selectedPhoto.id
  );

  const hasPrevious = photos.length > 1;
  const hasNext = photos.length > 1;

  const handleOpenLocation = async () => {
    try {
      await openPhotoLocation(selectedPhoto.id);
    } catch (error) {
      window.alert(
        error.message || "Unable to open the photo location."
      );
    }
  };

  const handleOverlayClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="photo-viewer-overlay"
      onMouseDown={handleOverlayClick}
    >
      <div
        className="photo-viewer-modal"
        onMouseDown={(event) => event.stopPropagation()}
      >
        {/* Close */}
        <button
          type="button"
          className="photo-viewer-close"
          onClick={onClose}
          aria-label="Close photo"
        >
          <X size={21} />
        </button>

        {/* Image area */}
        <div className="photo-viewer-stage">
          {hasPrevious && (
            <button
              type="button"
              className="photo-viewer-arrow photo-viewer-arrow-left"
              onClick={onPrevious}
              aria-label="Previous photo"
              disabled={currentIndex === -1}
            >
              <ChevronLeft size={25} />
            </button>
          )}

          <div className="photo-viewer-image-wrap">
            <img
              src={getPhotoImageUrl(selectedPhoto.id)}
              alt={selectedPhoto.filename}
              className="photo-viewer-image"
            />
          </div>

          {hasNext && (
            <button
              type="button"
              className="photo-viewer-arrow photo-viewer-arrow-right"
              onClick={onNext}
              aria-label="Next photo"
              disabled={currentIndex === -1}
            >
              <ChevronRight size={25} />
            </button>
          )}
        </div>

        {/* Information area */}
        <div className="photo-viewer-info">
          <div className="photo-viewer-details">
            <h2>{selectedPhoto.filename}</h2>

            <div className="photo-viewer-meta">
              {selectedPhoto.date_taken && (
                <span>{selectedPhoto.date_taken}</span>
              )}

              {selectedPhoto.camera && (
                <span>{selectedPhoto.camera}</span>
              )}

              {selectedPhoto.location_name && (
                <span>{selectedPhoto.location_name}</span>
              )}
            </div>
          </div>

          <button
            type="button"
            className="photo-viewer-location-button"
            onClick={handleOpenLocation}
          >
            <FolderOpen size={16} />
            <span>Open file location</span>
          </button>
        </div>
      </div>
    </div>
  );
}
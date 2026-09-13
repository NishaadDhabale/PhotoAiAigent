import { useCallback, useEffect, useMemo, useState } from "react";
import { Images, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

import SearchBar from "../components/search/SearchBar";
import PhotoGrid from "../components/photos/PhotoGrid";
import PhotoViewer from "../components/photos/PhotoViewer";

import LoadingState from "../components/common/LoadingState";
import EmptyState from "../components/common/EmptyState";
import ErrorState from "../components/common/ErrorState";

import { getPhotos, searchPhotos } from "../api/photoApi";

export default function PhotosPage() {
  const [photos, setPhotos] = useState([]);
  const [query, setQuery] = useState("");
  const [searched, setSearched] = useState(false);

  const [selectedPhoto, setSelectedPhoto] = useState(null);

  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);

  const loadPhotos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setSearched(false);

      const data = await getPhotos();

      setPhotos(data.results || []);
    } catch (err) {
      setError(
        err.message || "Unable to load photos."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPhotos();
  }, [loadPhotos]);

  const handleSearch = async () => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      loadPhotos();
      return;
    }

    try {
      setSearching(true);
      setError(null);
      setSearched(true);

      const data = await searchPhotos({
        query: trimmedQuery,
        n_results: 100,
      });

      setPhotos(data.results || []);
      setSelectedPhoto(null);
    } catch (err) {
      setError(
        err.message || "Search failed."
      );
    } finally {
      setSearching(false);
    }
  };

  const handleClearSearch = () => {
    setQuery("");
    setSelectedPhoto(null);
    loadPhotos();
  };

  const currentIndex = useMemo(() => {
    if (!selectedPhoto) {
      return -1;
    }

    return photos.findIndex(
      (photo) =>
        photo.id === selectedPhoto.id
    );
  }, [photos, selectedPhoto]);

  const handleNext = useCallback(() => {
    if (
      !photos.length ||
      currentIndex === -1
    ) {
      return;
    }

    const nextIndex =
      (currentIndex + 1) %
      photos.length;

    setSelectedPhoto(
      photos[nextIndex]
    );
  }, [photos, currentIndex]);

  const handlePrevious = useCallback(() => {
    if (
      !photos.length ||
      currentIndex === -1
    ) {
      return;
    }

    const previousIndex =
      (currentIndex - 1 + photos.length) %
      photos.length;

    setSelectedPhoto(
      photos[previousIndex]
    );
  }, [photos, currentIndex]);

  return (
    <div className="photos-page">

      {/* =========================
          HERO
      ========================== */}

      <section className="library-hero">
        <div className="hero-copy">

          <motion.div
            className="hero-eyebrow"
            initial={{
              opacity: 0,
              x: -8,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
          >
            <Sparkles size={15} />

            AI-powered photo library
          </motion.div>

          <motion.h1
            initial={{
              opacity: 0,
              y: 10,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
          >
            Your photos,
            <br />
            <span>
              beautifully organized.
            </span>
          </motion.h1>

          <motion.p
            initial={{
              opacity: 0,
              y: 10,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: 0.05,
            }}
          >
            Search your personal photo
            collection using people,
            places, dates, or natural
            language.
          </motion.p>

        </div>

        <motion.div
          className="hero-stat"
          initial={{
            opacity: 0,
            scale: 0.9,
          }}
          animate={{
            opacity: 1,
            scale: 1,
          }}
        >
          <Images size={20} />

          <strong>
            {photos.length}
          </strong>

          <span>
            {searched
              ? "matching photos"
              : "photos"}
          </span>
        </motion.div>
      </section>

      {/* =========================
          SEARCH
      ========================== */}

      <section className="photos-search-section">
        <SearchBar
          value={query}
          onChange={setQuery}
          onSubmit={handleSearch}
          onClear={handleClearSearch}
          loading={searching}
        />
      </section>

      {/* =========================
          CONTENT
      ========================== */}

      <main className="photos-content">

        {error ? (
          <ErrorState
            message={error}
            onRetry={
              searched
                ? handleSearch
                : loadPhotos
            }
          />
        ) : loading ? (
          <LoadingState />
        ) : photos.length === 0 ? (
          <EmptyState
            searching={searched}
            onClear={
              searched
                ? handleClearSearch
                : undefined
            }
          />
        ) : (
          <section className="library-section">

            <div className="library-heading">

              <div>
                <span className="section-label">
                  {searched
                    ? "SEARCH RESULTS"
                    : "LIBRARY"}
                </span>

                <h2>
                  {searched
                    ? "Matching photos"
                    : "All photos"}
                </h2>
              </div>

              <span className="result-count">
                {photos.length}{" "}
                {photos.length === 1
                  ? "photo"
                  : "photos"}
              </span>

            </div>

            <PhotoGrid
              photos={photos}
              onPhotoClick={
                setSelectedPhoto
              }
            />

          </section>
        )}

      </main>

      {/* =========================
          PHOTO VIEWER
      ========================== */}

      <PhotoViewer
        photos={photos}
        selectedPhoto={selectedPhoto}
        onClose={() =>
          setSelectedPhoto(null)
        }
        onNext={handleNext}
        onPrevious={handlePrevious}
      />

    </div>
  );
}
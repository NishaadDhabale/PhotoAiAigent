import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  Compass,
  Images,
  MapPin,
  Navigation,
} from "lucide-react";
import { motion } from "framer-motion";

import PhotoGrid from "../components/photos/PhotoGrid";
import PhotoViewer from "../components/photos/PhotoViewer";
import LoadingState from "../components/common/LoadingState";
import EmptyState from "../components/common/EmptyState";
import ErrorState from "../components/common/ErrorState";
import config from "../config/config";

import {
  getPlaces,
  getPlacePhotos,
  getUnknownPlacePhotos,
} from "../api/photoApi";


export default function PlacesPage() {
  const [places, setPlaces] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [placePhotos, setPlacePhotos] = useState([]);

  const [loading, setLoading] = useState(true);
  const [loadingPlace, setLoadingPlace] = useState(false);
  const [error, setError] = useState(null);

  const [selectedPhoto, setSelectedPhoto] = useState(null);


  const loadPlaces = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await getPlaces();

      setPlaces(data);
    } catch (err) {
      setError(
        err.message || "Unable to load places."
      );
    } finally {
      setLoading(false);
    }
  }, []);


  useEffect(() => {
    loadPlaces();
  }, [loadPlaces]);


  const openPlace = async (place) => {
    try {
      setLoadingPlace(true);
      setError(null);

      const data = await getPlacePhotos(
        place.location_name
      );

      setSelectedPlace(place);
      setPlacePhotos(data.results || []);
      setSelectedPhoto(null);
    } catch (err) {
      setError(
        err.message || "Unable to load place photos."
      );
    } finally {
      setLoadingPlace(false);
    }
  };


  const openUnknown = async () => {
    try {
      setLoadingPlace(true);
      setError(null);

      const data =
        await getUnknownPlacePhotos();

      setSelectedPlace({
        location_name: "Unknown location",
        photo_count: data.count,
      });

      setPlacePhotos(data.results || []);
      setSelectedPhoto(null);
    } catch (err) {
      setError(
        err.message ||
          "Unable to load photos without locations."
      );
    } finally {
      setLoadingPlace(false);
    }
  };


  const closePlace = () => {
    setSelectedPlace(null);
    setPlacePhotos([]);
    setSelectedPhoto(null);
  };


  const currentIndex = useMemo(() => {
    if (!selectedPhoto) {
      return -1;
    }

    return placePhotos.findIndex(
      (photo) =>
        photo.id === selectedPhoto.id
    );
  }, [placePhotos, selectedPhoto]);


  const handleNext = useCallback(() => {
    if (
      !placePhotos.length ||
      currentIndex === -1
    ) {
      return;
    }

    const nextIndex =
      (currentIndex + 1) %
      placePhotos.length;

    setSelectedPhoto(
      placePhotos[nextIndex]
    );
  }, [placePhotos, currentIndex]);


  const handlePrevious = useCallback(() => {
    if (
      !placePhotos.length ||
      currentIndex === -1
    ) {
      return;
    }

    const previousIndex =
      (currentIndex - 1 + placePhotos.length) %
      placePhotos.length;

    setSelectedPhoto(
      placePhotos[previousIndex]
    );
  }, [placePhotos, currentIndex]);


  if (loading) {
    return (
      <div className="places-page">
        <LoadingState />
      </div>
    );
  }


  if (error && !places) {
    return (
      <div className="places-page">
        <ErrorState
          message={error}
          onRetry={loadPlaces}
        />
      </div>
    );
  }


  if (selectedPlace) {
    return (
      <div className="places-page">

        <motion.div
          className="place-detail-header"
          initial={{
            opacity: 0,
            y: -8,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
        >

          <button
            type="button"
            className="back-button"
            onClick={closePlace}
          >
            <ArrowLeft size={17} />
            All places
          </button>

          <div className="place-detail-heading">

            <div className="place-detail-icon">
              {selectedPlace.location_name ===
              "Unknown location" ? (
                <Compass size={24} />
              ) : (
                <MapPin size={24} />
              )}
            </div>

            <div>
              <span className="section-label">
                PLACE
              </span>

              <h1>
                {selectedPlace.location_name}
              </h1>

              <p>
                {placePhotos.length}{" "}
                {placePhotos.length === 1
                  ? "photo"
                  : "photos"}
              </p>
            </div>

          </div>

        </motion.div>


        {loadingPlace ? (
          <LoadingState />
        ) : placePhotos.length === 0 ? (
          <EmptyState />
        ) : (
          <section className="place-photo-section">

            <PhotoGrid
              photos={placePhotos}
              onPhotoClick={
                setSelectedPhoto
              }
            />

          </section>
        )}


        <PhotoViewer
          photos={placePhotos}
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


  if (!places || places.total_photos === 0) {
    return (
      <div className="places-page">
        <EmptyState />
      </div>
    );
  }


  return (
    <div className="places-page">

      {/* HERO */}

      <section className="places-hero">

        <div className="places-hero-copy">

          <motion.div
            className="places-eyebrow"
            initial={{
              opacity: 0,
              x: -8,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
          >
            <MapPin size={15} />
            Your photo map
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
            Memories,
            <br />
            <span>by place.</span>
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
            Explore your photos through
            the places where they were captured.
          </motion.p>

        </div>


        <motion.div
          className="places-stats"
          initial={{
            opacity: 0,
            scale: 0.92,
          }}
          animate={{
            opacity: 1,
            scale: 1,
          }}
        >

          <div className="places-stat">
            <Images size={18} />
            <strong>
              {places.total_photos}
            </strong>
            <span>photos</span>
          </div>

          <div className="places-stat">
            <Navigation size={18} />
            <strong>
              {places.located_photos}
            </strong>
            <span>located</span>
          </div>

          <div className="places-stat">
            <Compass size={18} />
            <strong>
              {places.count}
            </strong>
            <span>places</span>
          </div>

        </motion.div>

      </section>


      {/* PLACES */}

      {places.results.length > 0 && (
        <section className="places-section">

          <div className="places-section-header">
            <div>
              <span className="section-label">
                LOCATIONS
              </span>

              <h2>
                Places in your library
              </h2>
            </div>

            <span className="result-count">
              {places.count}{" "}
              {places.count === 1
                ? "place"
                : "places"}
            </span>
          </div>


          <div className="places-grid">

            {places.results.map(
              (place, index) => (
                <motion.button
                  key={place.location_name}
                  type="button"
                  className="place-card"
                  onClick={() =>
                    openPlace(place)
                  }
                  initial={{
                    opacity: 0,
                    y: 18,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{
                    duration: 0.3,
                    delay: Math.min(
                      index * 0.035,
                      0.35
                    ),
                  }}
                  whileHover={{
                    y: -5,
                  }}
                  whileTap={{
                    scale: 0.985,
                  }}
                >

                  <div className="place-card-image">

                    {place.representative_image_url ? (
                      <img
                        src={
                          place.representative_image_url.startsWith(
                            "http"
                          )
                            ? place.representative_image_url
                            : `${config.apiBaseUrl}${place.representative_image_url}`
                        }
                        alt=""
                        loading="lazy"
                      />
                    ) : (
                      <div className="place-card-placeholder">
                        <MapPin size={28} />
                      </div>
                    )}

                    <div className="place-card-overlay">
                      <span>
                        Explore photos
                      </span>
                    </div>

                  </div>


                  <div className="place-card-info">

                    <div className="place-card-name">
                      <MapPin size={15} />
                      <span
                        title={
                          place.location_name
                        }
                      >
                        {place.location_name}
                      </span>
                    </div>

                    <span className="place-card-count">
                      {place.photo_count}{" "}
                      {place.photo_count === 1
                        ? "photo"
                        : "photos"}
                    </span>

                  </div>

                </motion.button>
              )
            )}

          </div>

        </section>
      )}


      {/* UNKNOWN */}

      {places.unknown_photos > 0 && (
        <section className="places-section places-unknown-section">

          <div className="places-section-header">

            <div>
              <span className="section-label">
                NEEDS LOCATION DATA
              </span>

              <h2>
                Unknown location
              </h2>

              <p className="places-section-description">
                These photos don't currently
                contain a recognized location.
              </p>
            </div>

            <span className="result-count">
              {places.unknown_photos}{" "}
              {places.unknown_photos === 1
                ? "photo"
                : "photos"}
            </span>

          </div>


          <motion.button
            type="button"
            className="unknown-place-card"
            onClick={openUnknown}
            whileHover={{
              y: -3,
            }}
            whileTap={{
              scale: 0.99,
            }}
          >

            <div className="unknown-place-icon">
              <Compass size={26} />
            </div>

            <div>
              <strong>
                Browse photos without
                location data
              </strong>

              <span>
                {places.unknown_photos} photos
              </span>
            </div>

            <ArrowLeft
              size={18}
              className="unknown-place-arrow"
            />

          </motion.button>

        </section>
      )}

    </div>
  );
}
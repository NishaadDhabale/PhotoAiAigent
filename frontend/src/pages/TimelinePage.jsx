import { useCallback, useEffect, useMemo, useState } from "react";
import { CalendarDays, Clock3, Images } from "lucide-react";
import { motion } from "framer-motion";

import PhotoGrid from "../components/photos/PhotoGrid";
import PhotoViewer from "../components/photos/PhotoViewer";
import LoadingState from "../components/common/LoadingState";
import EmptyState from "../components/common/EmptyState";
import ErrorState from "../components/common/ErrorState";

import { getTimeline } from "../api/photoApi";

export default function TimelinePage() {
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPhoto, setSelectedPhoto] = useState(null);

  const loadTimeline = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await getTimeline();

      setTimeline(data);
    } catch (err) {
      setError(
        err.message || "Unable to load timeline."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTimeline();
  }, [loadTimeline]);

  const allPhotos = useMemo(() => {
    if (!timeline) {
      return [];
    }

    const photos = [];

    for (const year of timeline.years || []) {
      for (const month of year.months || []) {
        photos.push(...(month.results || []));
      }
    }

    photos.push(...(timeline.undated || []));

    return photos;
  }, [timeline]);

  const currentIndex = useMemo(() => {
    if (!selectedPhoto) {
      return -1;
    }

    return allPhotos.findIndex(
      (photo) => photo.id === selectedPhoto.id
    );
  }, [allPhotos, selectedPhoto]);

  const handleNext = useCallback(() => {
    if (
      !allPhotos.length ||
      currentIndex === -1
    ) {
      return;
    }

    const nextIndex =
      (currentIndex + 1) % allPhotos.length;

    setSelectedPhoto(allPhotos[nextIndex]);
  }, [allPhotos, currentIndex]);

  const handlePrevious = useCallback(() => {
    if (
      !allPhotos.length ||
      currentIndex === -1
    ) {
      return;
    }

    const previousIndex =
      (currentIndex - 1 + allPhotos.length) %
      allPhotos.length;

    setSelectedPhoto(allPhotos[previousIndex]);
  }, [allPhotos, currentIndex]);

  if (loading) {
    return (
      <div className="timeline-page">
        <LoadingState />
      </div>
    );
  }

  if (error) {
    return (
      <div className="timeline-page">
        <ErrorState
          message={error}
          onRetry={loadTimeline}
        />
      </div>
    );
  }

  if (!timeline || timeline.total_photos === 0) {
    return (
      <div className="timeline-page">
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="timeline-page">

      {/* HERO */}

      <section className="timeline-hero">

        <div className="timeline-hero-copy">

          <motion.div
            className="timeline-eyebrow"
            initial={{
              opacity: 0,
              x: -8,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
          >
            <CalendarDays size={15} />
            Your visual timeline
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
            Your memories,
            <br />
            <span>across time.</span>
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
            Browse your photo collection
            chronologically, from the latest
            memories back through the years.
          </motion.p>

        </div>

        <motion.div
          className="timeline-stats"
          initial={{
            opacity: 0,
            scale: 0.92,
          }}
          animate={{
            opacity: 1,
            scale: 1,
          }}
        >

          <div className="timeline-stat">
            <Images size={18} />
            <strong>
              {timeline.total_photos}
            </strong>
            <span>photos</span>
          </div>

          <div className="timeline-stat">
            <CalendarDays size={18} />
            <strong>
              {timeline.years.length}
            </strong>
            <span>years</span>
          </div>

          <div className="timeline-stat">
            <Clock3 size={18} />
            <strong>
              {timeline.undated_photos}
            </strong>
            <span>undated</span>
          </div>

        </motion.div>

      </section>

      {/* TIMELINE */}

      <section className="timeline-content">

        {(timeline.years || []).map(
          (year, yearIndex) => (
            <motion.section
              className="timeline-year"
              key={year.year}
              initial={{
                opacity: 0,
                y: 20,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              transition={{
                duration: 0.35,
                delay: Math.min(
                  yearIndex * 0.06,
                  0.3
                ),
              }}
            >

              <div className="timeline-year-header">

                <div className="timeline-year-title">
                  <span className="timeline-year-dot" />
                  <h2>{year.year}</h2>
                </div>

                <span className="timeline-year-count">
                  {year.count}{" "}
                  {year.count === 1
                    ? "photo"
                    : "photos"}
                </span>

              </div>

              <div className="timeline-year-line" />

              {(year.months || []).map(
                (month) => (
                  <section
                    className="timeline-month"
                    key={`${year.year}-${month.month}`}
                  >

                    <div className="timeline-month-header">

                      <div>
                        <span className="section-label">
                          {year.year}
                        </span>

                        <h3>
                          {month.month_name}
                        </h3>
                      </div>

                      <span className="timeline-month-count">
                        {month.count}
                      </span>

                    </div>

                    <PhotoGrid
                      photos={month.results}
                      onPhotoClick={
                        setSelectedPhoto
                      }
                    />

                  </section>
                )
              )}

            </motion.section>
          )
        )}

        {/* UNDATED */}

        {timeline.undated?.length > 0 && (
          <motion.section
            className="timeline-undated"
            initial={{
              opacity: 0,
              y: 20,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
          >

            <div className="timeline-year-header">

              <div className="timeline-year-title">
                <span className="timeline-year-dot" />
                <h2>No date</h2>
              </div>

              <span className="timeline-year-count">
                {timeline.undated.length}{" "}
                {timeline.undated.length === 1
                  ? "photo"
                  : "photos"}
              </span>

            </div>

            <div className="timeline-year-line" />

            <div className="timeline-undated-description">
              These photos don't contain a recorded
              capture date.
            </div>

            <PhotoGrid
              photos={timeline.undated}
              onPhotoClick={setSelectedPhoto}
            />

          </motion.section>
        )}

      </section>

      <PhotoViewer
        photos={allPhotos}
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
import { useEffect, useState } from "react";
import { Copy, RefreshCw, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { getDuplicates, getPhotoImageUrl } from "../api/photoApi";
import "./DuplicatesPage.css";

export default function DuplicatesPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDuplicates = async () => {
    try {
      setLoading(true);
      setError("");
      const result = await getDuplicates();
      setData(result);
    } catch (err) {
      console.error(err);
      setError("Failed to scan for duplicates.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDuplicates();
  }, []);

  if (loading) {
    return (
      <div className="duplicates-page">
        <div className="page-loading">
          <RefreshCw className="spin" size={24} />
          <span>Scanning your photos for duplicates...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="duplicates-page">
        <div className="error-card">
          <AlertTriangle size={24} />
          <span>{error}</span>
          <button onClick={loadDuplicates}>Try again</button>
        </div>
      </div>
    );
  }

  return (
    <div className="duplicates-page">
      <div className="duplicates-header">
        <div>
          <div className="duplicates-title">
            <Copy size={30} />
            <div>
              <h1>Duplicate Photos</h1>
              <p>Find exact and visually similar photos in your library.</p>
            </div>
          </div>
        </div>

        <button className="refresh-button" onClick={loadDuplicates}>
          <RefreshCw size={17} />
          Rescan
        </button>
      </div>

      <div className="duplicate-stats">
        <StatCard
          label="Photos scanned"
          value={data.total_photos}
        />
        <StatCard
          label="Exact groups"
          value={data.exact_group_count}
        />
        <StatCard
          label="Duplicate photos"
          value={data.exact_duplicate_photo_count}
        />
        <StatCard
          label="Near duplicates"
          value={data.near_duplicate_count}
        />
      </div>

      {data.exact_groups.length === 0 &&
      data.near_duplicates.length === 0 ? (
        <div className="empty-duplicates">
          <Copy size={46} />
          <h2>No duplicates found</h2>
          <p>
            Your current photo library does not contain any exact or
            high-similarity duplicate candidates.
          </p>
        </div>
      ) : (
        <>
          {data.exact_groups.length > 0 && (
            <section className="duplicate-section">
              <h2>Exact duplicates</h2>

              <div className="duplicate-groups">
                {data.exact_groups.map((group) => (
                  <motion.div
                    key={group.group_id}
                    className="duplicate-group"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <div className="group-header">
                      <strong>Group {group.group_id}</strong>
                      <span>{group.count} identical photos</span>
                    </div>

                    <div className="duplicate-grid">
                      {group.photos.map((photo) => (
                        <PhotoCard
                          key={photo.id}
                          photo={photo}
                        />
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </section>
          )}

          {data.near_duplicates.length > 0 && (
            <section className="duplicate-section">
              <h2>Near-duplicate candidates</h2>
              <p className="section-description">
                These photos have very similar visual embeddings. Review them
                before deciding whether they are actually duplicates.
              </p>

              <div className="near-duplicate-list">
                {data.near_duplicates.map((pair, index) => (
                  <motion.div
                    key={`${pair.photo_a.id}-${pair.photo_b.id}`}
                    className="near-duplicate-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.03 }}
                  >
                    <PhotoCard photo={pair.photo_a} />
                    <div className="similarity">
                      <strong>
                        {(pair.similarity * 100).toFixed(1)}%
                      </strong>
                      <span>similar</span>
                    </div>
                    <PhotoCard photo={pair.photo_b} />
                  </motion.div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="duplicate-stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function PhotoCard({ photo }) {
  return (
    <div className="duplicate-photo-card">
      <img
        src={getPhotoImageUrl(photo.id)}
        alt={photo.filename}
      />

      <div className="duplicate-photo-info">
        <strong title={photo.filename}>{photo.filename}</strong>

        {photo.date_taken && (
          <span>{photo.date_taken}</span>
        )}

        {photo.location_name && (
          <span>{photo.location_name}</span>
        )}
      </div>
    </div>
  );
}
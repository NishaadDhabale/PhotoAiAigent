import { useEffect,useRef, useState } from "react";
import {
  CheckCircle2,
  FolderTree,
  AlertTriangle,
  FileWarning,
  RefreshCw,
  ArrowRight,
  ShieldCheck,
  Move,
} from "lucide-react";
import { getOrganizationPreview, executeOrganization } from "../api/photoApi";
import "./OrganizationPanel.css";

function StatCard({ icon: Icon, label, value, tone = "default" }) {
  return (
    <div className={`organization-stat organization-stat-${tone}`}>
      <div className="organization-stat-icon">
        <Icon size={18} />
      </div>

      <div>
        <strong>{value}</strong>
        <span>{label}</span>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const config = {
    SAFE: {
      label: "Ready",
      className: "safe",
      icon: CheckCircle2,
    },
    CONFLICT: {
      label: "Conflict",
      className: "conflict",
      icon: AlertTriangle,
    },
    MISSING_SOURCE: {
      label: "Missing",
      className: "missing",
      icon: FileWarning,
    },
    ALREADY_ORGANIZED: {
      label: "Organized",
      className: "organized",
      icon: CheckCircle2,
    },
  };

  const item = config[status] || {
    label: status,
    className: "default",
    icon: FileWarning,
  };

  const Icon = item.icon;

  return (
    <span className={`organization-status ${item.className}`}>
      <Icon size={13} />
      {item.label}
    </span>
  );
}

export default function OrganizationPanel() {
  const organizationSectionRef = useRef(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);

  async function loadPreview() {
    try {
      setLoading(true);
      setError("");
      setResult(null);

      const response = await getOrganizationPreview();
      setData(response);
    } catch (err) {
      setError(err.message || "Failed to load organization preview.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPreview();
  }, []);

  async function handleExecute() {
    try {
      setExecuting(true);
      setError("");
      setShowConfirmation(false);

      const response = await executeOrganization(true);
      setResult(response);

      await loadPreview();
    } catch (err) {
      setError(err.message || "Organization failed.");
    } finally {
      setExecuting(false);
    }
  }

  if (loading) {
    return (
      <div className="organization-page">
        <div className="organization-loading">
          <RefreshCw size={22} className="organization-spinner" />
          <p>Preparing organization preview...</p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="organization-page">
        <div className="organization-error">
          <div className="organization-error-icon">
            <AlertTriangle size={22} />
          </div>

          <h2>Unable to load organization</h2>
          <p>{error}</p>

          <button
            type="button"
            className="organization-secondary-button"
            onClick={loadPreview}
          >
            <RefreshCw size={15} />
            Try again
          </button>
        </div>
      </div>
    );
  }

  const summary = data?.summary || {};
  const plan = data?.plan || [];

  const canOrganize =
    summary.safe > 0 &&
    summary.conflicts === 0 &&
    summary.missing_source === 0;

  return (
    <div className="organization-page">

      {/* HERO */}
      <section className="organization-hero">
        <div className="organization-hero-copy">
          <div className="organization-eyebrow">
            <FolderTree size={14} />
            Library organization
          </div>

          <h1>
            Organize your
            <span> photo library.</span>
          </h1>

          <p>
            PhotoAgent can safely arrange your photos into year-based folders
            without overwriting existing files or losing your library data.
          </p>
        </div>

        <div className="organization-hero-stat">
          <strong>{summary.photos ?? 0}</strong>
          <span>photos scanned</span>
        </div>
      </section>

      {/* SAFETY BANNER */}
      <section
      id="organization-section"
  ref={organizationSectionRef}
  className="organization-content"
>

        <div className="organization-safety">
          <div className="organization-safety-icon">
            <ShieldCheck size={21} />
          </div>

          <div className="organization-safety-copy">
            <strong>Safe organization</strong>
            <span>
              Files are never overwritten. PhotoAgent checks the entire plan
              before moving anything.
            </span>
          </div>

          <div className="organization-safety-label">
            Protected
          </div>
        </div>

        {/* STATS */}
        <div className="organization-stats">
          <StatCard
            icon={CheckCircle2}
            label="Ready to move"
            value={summary.safe ?? 0}
            tone="success"
          />

          <StatCard
            icon={AlertTriangle}
            label="Conflicts"
            value={summary.conflicts ?? 0}
            tone={summary.conflicts ? "danger" : "default"}
          />

          <StatCard
            icon={CheckCircle2}
            label="Already organized"
            value={summary.already_organized ?? 0}
          />

          <StatCard
            icon={FileWarning}
            label="Missing files"
            value={summary.missing_source ?? 0}
            tone={summary.missing_source ? "danger" : "default"}
          />
        </div>

        {/* PREVIEW */}
        <div className="organization-section-header">
          <div>
            <span className="organization-section-label">PREVIEW</span>
            <h2>Proposed changes</h2>
            <p>
              Nothing has been changed yet. Review where each photo will go.
            </p>
          </div>

          <button
            type="button"
            className="organization-refresh"
            onClick={loadPreview}
            disabled={loading || executing}
          >
            <RefreshCw size={15} />
            Refresh
          </button>
        </div>

        <div className="organization-plan">
          {plan.length === 0 ? (
            <div className="organization-empty">
              <FolderTree size={24} />
              <h3>Nothing to organize</h3>
              <p>Your photo library is already organized.</p>
            </div>
          ) : (
            Object.entries(
              plan.reduce((groups, item) => {
                if (!groups[item.year]) {
                  groups[item.year] = [];
                }

                groups[item.year].push(item);
                return groups;
              }, {})
            ).map(([year, items]) => (
              <div className="organization-year" key={year}>

                <div className="organization-year-header">
                  <div className="organization-year-title">
                    <FolderTree size={17} />
                    <strong>{year}</strong>
                  </div>

                  <span>
                    {items.length} {items.length === 1 ? "photo" : "photos"}
                  </span>
                </div>

                <div className="organization-files">
                  {items.map((item) => (
                    <div
                      className={`organization-file organization-file-${item.status.toLowerCase()}`}
                      key={item.photo_id}
                    >
                      <div className="organization-file-main">
                        <div className="organization-file-icon">
                          <Move size={16} />
                        </div>

                        <div className="organization-file-name">
                          <strong>{item.filename}</strong>

                          <div className="organization-file-path">
                            <span>{item.source}</span>

                            {item.status === "SAFE" && (
                              <>
                                <ArrowRight size={13} />
                                <span>{item.destination}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      <StatusBadge status={item.status} />
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* ERROR */}
        {error && (
          <div className="organization-inline-error">
            <AlertTriangle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* SUCCESS */}
        {result && (
          <div className="organization-success">
            <div className="organization-success-icon">
              <CheckCircle2 size={19} />
            </div>

            <div>
              <strong>Library organized successfully</strong>
              <span>
                {result.count}{" "}
                {result.count === 1 ? "photo was" : "photos were"} processed.
              </span>
            </div>
          </div>
        )}

        {/* ACTION */}
        <div className="organization-action">
          <div>
            <strong>Ready to organize?</strong>
            <span>
              This will move only the photos marked as safe.
            </span>
          </div>

          <button
  type="button"
  className="organization-primary-button"
  disabled={!canOrganize || executing}
  onClick={() => {
    organizationSectionRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }}
>
            {executing ? (
              <>
                <RefreshCw size={16} className="organization-spinner" />
                Organizing...
              </>
            ) : (
              <>
                <Move size={16} />
                Organize library
              </>
            )}
          </button>
        </div>
      </section>

      {/* CONFIRMATION MODAL */}
      {showConfirmation && (
        <div
          className="organization-modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setShowConfirmation(false);
            }
          }}
        >
          <div className="organization-modal">
            <div className="organization-modal-icon">
              <ShieldCheck size={24} />
            </div>

            <h2>Organize your library?</h2>

            <p>
              PhotoAgent will move{" "}
              <strong>{summary.safe}</strong>{" "}
              {summary.safe === 1 ? "photo" : "photos"} into year-based
              folders.
            </p>

            <div className="organization-modal-warning">
              <CheckCircle2 size={16} />
              <span>
                Existing files will never be overwritten.
              </span>
            </div>

            <div className="organization-modal-actions">
              <button
                type="button"
                className="organization-secondary-button"
                onClick={() => setShowConfirmation(false)}
                disabled={executing}
              >
                Cancel
              </button>

              <button
                type="button"
                className="organization-primary-button"
                onClick={handleExecute}
                disabled={executing}
              >
                <Move size={16} />
                Confirm & organize
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
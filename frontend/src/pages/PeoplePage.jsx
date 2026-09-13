import { useCallback, useEffect, useState } from "react";
import {
  Users,
  UserRound,
  Sparkles,
  Check,
  X,
  Merge,
  Pencil,
  MapPin,
} from "lucide-react";
import { motion } from "framer-motion";

import PersonCard from "../components/people/PersonCard";
import PersonDetail from "../components/people/PersonDetail";
import PhotoViewer from "../components/photos/PhotoViewer";

import {
  getPeople,
  renamePerson,
  mergePeople,
  getPhotoImageUrl,
} from "../api/photoApi";

export default function PeoplePage() {
  const [personPhotos, setPersonPhotos] = useState([]);
  const [people, setPeople] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [selectedPhoto, setSelectedPhoto] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ---------------------------------------------------------
  // MANAGEMENT STATE
  // ---------------------------------------------------------

  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedGroups, setSelectedGroups] = useState([]);

  const [renamingPerson, setRenamingPerson] = useState(null);
  const [renameValue, setRenameValue] = useState("");
  const [savingName, setSavingName] = useState(false);

  const [showMergeConfirm, setShowMergeConfirm] = useState(false);
  const [merging, setMerging] = useState(false);

  const [actionError, setActionError] = useState("");

  // ---------------------------------------------------------
  // LOAD PEOPLE
  // ---------------------------------------------------------

  const loadPeople = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await getPeople();
      setPeople(data.results || []);
    } catch (err) {
      setError(err.message || "Unable to load people.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPeople();
  }, [loadPeople]);

  // ---------------------------------------------------------
  // RENAME
  // ---------------------------------------------------------

  function startRename(person) {
    setActionError("");
    setRenamingPerson(person);
    setRenameValue(person.name || "");
  }

  function cancelRename() {
    setRenamingPerson(null);
    setRenameValue("");
    setActionError("");
  }

  async function saveRename() {
    if (!renamingPerson) {
      return;
    }

    const name = renameValue.trim();

    if (!name) {
      setActionError("Person name cannot be empty.");
      return;
    }

    const groupId = renamingPerson.group_id;

    if (groupId === undefined || groupId === null) {
      setActionError(
        "Unable to determine the selected person's group."
      );
      return;
    }

    try {
      setSavingName(true);
      setActionError("");

      await renamePerson(groupId, name);

      // Update the people list immediately.
      setPeople((currentPeople) =>
        currentPeople.map((person) =>
          person.group_id === groupId
            ? {
                ...person,
                name,
              }
            : person
        )
      );

      // If this person is currently open, update that too.
      if (
        selectedPerson &&
        selectedPerson.group_id === groupId
      ) {
        setSelectedPerson({
          ...selectedPerson,
          name,
        });
      }

      cancelRename();
    } catch (err) {
      setActionError(
        err.message || "Failed to rename person."
      );
    } finally {
      setSavingName(false);
    }
  }

  // ---------------------------------------------------------
  // GROUP SELECTION
  // ---------------------------------------------------------

  function toggleGroupSelection(person) {
    const groupId = person.group_id;

    setSelectedGroups((current) => {
      if (current.includes(groupId)) {
        return current.filter((id) => id !== groupId);
      }

      return [...current, groupId];
    });
  }

  function isGroupSelected(person) {
    return selectedGroups.includes(person.group_id);
  }

  function cancelSelectionMode() {
    setSelectionMode(false);
    setSelectedGroups([]);
    setShowMergeConfirm(false);
    setActionError("");
  }

  function beginMerge() {
    if (selectedGroups.length < 2) {
      setActionError(
        "Select at least two people to merge."
      );
      return;
    }

    setActionError("");
    setShowMergeConfirm(true);
  }

  // ---------------------------------------------------------
  // MERGE
  // ---------------------------------------------------------

  async function confirmMerge() {
    if (selectedGroups.length < 2) {
      return;
    }

    try {
      setMerging(true);
      setActionError("");

      // The first selected group becomes the surviving group.
      const targetGroupId = selectedGroups[0];

      await mergePeople(
        selectedGroups,
        targetGroupId
      );

      setShowMergeConfirm(false);
      setSelectionMode(false);
      setSelectedGroups([]);

      // Reload from SQLite so the UI reflects the database.
      await loadPeople();
    } catch (err) {
      setActionError(
        err.message || "Failed to merge people."
      );
    } finally {
      setMerging(false);
    }
  }

  // ---------------------------------------------------------
  // DOUBLE CLICK PHOTO → LOCATION
  // ---------------------------------------------------------

  function handlePhotoDoubleClick(event) {
    const image = event.target.closest("img");

    if (!image) {
      return;
    }

    const photo = personPhotos.find(
      (item) =>
        getPhotoImageUrl(item.id) === image.src
    );

    if (!photo) {
      return;
    }

    const latitude = photo.latitude;
    const longitude = photo.longitude;

    if (
      latitude === null ||
      latitude === undefined ||
      longitude === null ||
      longitude === undefined
    ) {
      setActionError(
        `No location is available for ${photo.filename}.`
      );

      return;
    }

    const mapsUrl =
      "https://www.google.com/maps/search/?api=1&query=" +
      `${latitude},${longitude}`;

    window.open(
      mapsUrl,
      "_blank",
      "noopener,noreferrer"
    );
  }

  // ---------------------------------------------------------
  // PAGE
  // ---------------------------------------------------------

  return (
    <div
      className="people-page"
      onDoubleClick={handlePhotoDoubleClick}
    >
      {!selectedPerson ? (
        <>
          {/* -------------------------------------------------
              HERO
          ------------------------------------------------- */}

          <section className="people-hero">
            <div>
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
                Face recognition
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
                People
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
                People and face groups discovered across
                your photo library.
              </motion.p>
            </div>

            <div className="people-stat">
              <Users size={20} />

              <strong>{people.length}</strong>

              <span>
                {people.length === 1
                  ? "person found"
                  : "people found"}
              </span>
            </div>
          </section>

          {/* -------------------------------------------------
              MANAGEMENT BAR
          ------------------------------------------------- */}

          {!loading &&
            !error &&
            people.length > 0 && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  marginBottom: "20px",
                }}
              >
                {!selectionMode ? (
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => {
                      setSelectionMode(true);
                      setActionError("");
                    }}
                  >
                    <Merge size={15} />
                    Select people to merge
                  </button>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      flexWrap: "wrap",
                    }}
                  >
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={beginMerge}
                      disabled={
                        selectedGroups.length < 2
                      }
                    >
                      <Merge size={15} />
                      Mark as same person
                      {selectedGroups.length > 0 &&
                        ` (${selectedGroups.length})`}
                    </button>

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={cancelSelectionMode}
                    >
                      <X size={15} />
                      Cancel
                    </button>
                  </div>
                )}

                {actionError && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      color: "#b91c1c",
                      fontSize: "12px",
                    }}
                  >
                    <MapPin size={14} />
                    {actionError}
                  </div>
                )}
              </div>
            )}

          {/* -------------------------------------------------
              LOADING
          ------------------------------------------------- */}

          {loading && (
            <div className="people-loading-grid">
              {Array.from({ length: 8 }).map(
                (_, index) => (
                  <div
                    className="person-skeleton"
                    key={index}
                  >
                    <div className="person-skeleton-image" />
                    <div className="person-skeleton-line" />
                    <div className="person-skeleton-small" />
                  </div>
                )
              )}
            </div>
          )}

          {/* -------------------------------------------------
              ERROR
          ------------------------------------------------- */}

          {!loading && error && (
            <div className="people-error">
              <UserRound size={30} />

              <h2>Unable to load people</h2>

              <p>{error}</p>

              <button
                type="button"
                className="secondary-button"
                onClick={loadPeople}
              >
                Try again
              </button>
            </div>
          )}

          {/* -------------------------------------------------
              EMPTY
          ------------------------------------------------- */}

          {!loading &&
            !error &&
            people.length === 0 && (
              <div className="empty-state">
                <UserRound size={32} />

                <h2>No people detected</h2>

                <p>
                  Face detection has not found any
                  recognizable groups yet.
                </p>
              </div>
            )}

          {/* -------------------------------------------------
              PEOPLE GRID
          ------------------------------------------------- */}

          {!loading &&
            !error &&
            people.length > 0 && (
              <section className="people-section">
                <div className="library-heading">
                  <div>
                    <span className="section-label">
                      FACE GROUPS
                    </span>

                    <h2>People in your library</h2>
                  </div>

                  <span className="result-count">
                    {people.length} groups
                  </span>
                </div>

                <div className="people-grid">
                  {people.map((person, index) => {
                    const selected =
                      isGroupSelected(person);

                    return (
                      <div
                        key={person.group_id}
                        style={{
                          position: "relative",
                          outline: selected
                            ? "2px solid var(--primary)"
                            : "none",
                          outlineOffset: "3px",
                          borderRadius: "14px",
                        }}
                      >
                        {/* SELECTION CHECK */}

                        {selectionMode && (
                          <button
                            type="button"
                            onClick={(event) => {
                              event.stopPropagation();
                              toggleGroupSelection(
                                person
                              );
                            }}
                            style={{
                              position: "absolute",
                              top: "10px",
                              right: "10px",
                              zIndex: 5,
                              width: "30px",
                              height: "30px",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              border:
                                "1px solid var(--border)",
                              borderRadius: "50%",
                              background: selected
                                ? "var(--primary)"
                                : "var(--surface)",
                              color: selected
                                ? "white"
                                : "var(--text-secondary)",
                              cursor: "pointer",
                            }}
                          >
                            {selected && (
                              <Check size={16} />
                            )}
                          </button>
                        )}

                        {/* PERSON CARD */}

                        <PersonCard
                          person={person}
                          index={index}
                          onClick={() => {
                            if (selectionMode) {
                              toggleGroupSelection(
                                person
                              );
                              return;
                            }

                            setSelectedPerson(person);
                          }}
                        />

                        {/* RENAME BUTTON */}

                        {!selectionMode && (
                          <button
                            type="button"
                            onClick={(event) => {
                              event.stopPropagation();
                              startRename(person);
                            }}
                            style={{
                              position: "absolute",
                              bottom: "12px",
                              right: "12px",
                              zIndex: 5,
                              width: "32px",
                              height: "32px",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              border:
                                "1px solid var(--border)",
                              borderRadius: "9px",
                              background:
                                "var(--surface)",
                              color:
                                "var(--text-secondary)",
                              cursor: "pointer",
                              boxShadow:
                                "0 2px 8px rgba(0,0,0,0.08)",
                            }}
                            title="Rename person"
                          >
                            <Pencil size={14} />
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

          {/* -------------------------------------------------
              RENAME MODAL
          ------------------------------------------------- */}

          {renamingPerson && (
            <div
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "20px",
                background: "rgba(0,0,0,0.45)",
              }}
              onMouseDown={(event) => {
                if (
                  event.target === event.currentTarget
                ) {
                  cancelRename();
                }
              }}
            >
              <div
                style={{
                  width: "min(420px, 100%)",
                  padding: "25px",
                  border:
                    "1px solid var(--border)",
                  borderRadius: "16px",
                  background:
                    "var(--surface)",
                  boxShadow:
                    "var(--shadow-lg)",
                }}
              >
                <h2
                  style={{
                    margin: "0 0 8px",
                    fontSize: "20px",
                  }}
                >
                  Rename person
                </h2>

                <p
                  style={{
                    margin: "0 0 18px",
                    color: "var(--text-muted)",
                    fontSize: "12px",
                  }}
                >
                  Give this person a name.
                </p>

                <input
                  autoFocus
                  value={renameValue}
                  onChange={(event) =>
                    setRenameValue(
                      event.target.value
                    )
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      saveRename();
                    }

                    if (event.key === "Escape") {
                      cancelRename();
                    }
                  }}
                  placeholder="Person name"
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    height: "42px",
                    padding: "0 12px",
                    border:
                      "1px solid var(--border)",
                    borderRadius: "9px",
                    background:
                      "var(--surface)",
                    color:
                      "var(--text-primary)",
                    fontSize: "13px",
                    outline: "none",
                  }}
                />

                {actionError && (
                  <p
                    style={{
                      margin: "8px 0 0",
                      color: "#b91c1c",
                      fontSize: "11px",
                    }}
                  >
                    {actionError}
                  </p>
                )}

                <div
                  style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: "8px",
                    marginTop: "20px",
                  }}
                >
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={cancelRename}
                    disabled={savingName}
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    className="primary-button"
                    onClick={saveRename}
                    disabled={savingName}
                  >
                    {savingName
                      ? "Saving..."
                      : "Save name"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* -------------------------------------------------
              MERGE CONFIRMATION
          ------------------------------------------------- */}

          {showMergeConfirm && (
            <div
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 1000,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "20px",
                background: "rgba(0,0,0,0.45)",
              }}
              onMouseDown={(event) => {
                if (
                  event.target === event.currentTarget
                ) {
                  setShowMergeConfirm(false);
                }
              }}
            >
              <div
                style={{
                  width: "min(450px, 100%)",
                  padding: "26px",
                  border:
                    "1px solid var(--border)",
                  borderRadius: "16px",
                  background:
                    "var(--surface)",
                  boxShadow:
                    "var(--shadow-lg)",
                }}
              >
                <div
                  style={{
                    width: "46px",
                    height: "46px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: "16px",
                    borderRadius: "12px",
                    background:
                      "var(--surface-active)",
                  }}
                >
                  <Merge size={22} />
                </div>

                <h2
                  style={{
                    margin: "0 0 9px",
                    fontSize: "20px",
                  }}
                >
                  Mark as the same person?
                </h2>

                <p
                  style={{
                    margin: "0",
                    color:
                      "var(--text-secondary)",
                    fontSize: "12px",
                    lineHeight: "1.6",
                  }}
                >
                  You selected{" "}
                  <strong>
                    {selectedGroups.length}
                  </strong>{" "}
                  face groups. PhotoAgent will merge
                  them into one person group.
                </p>

                <p
                  style={{
                    margin: "12px 0 0",
                    color: "var(--text-muted)",
                    fontSize: "11px",
                    lineHeight: "1.6",
                  }}
                >
                  The first selected group will be
                  kept. Photos themselves will not be
                  deleted or modified.
                </p>

                {actionError && (
                  <p
                    style={{
                      margin: "12px 0 0",
                      color: "#b91c1c",
                      fontSize: "11px",
                    }}
                  >
                    {actionError}
                  </p>
                )}

                <div
                  style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: "8px",
                    marginTop: "24px",
                  }}
                >
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      setShowMergeConfirm(false)
                    }
                    disabled={merging}
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    className="primary-button"
                    onClick={confirmMerge}
                    disabled={merging}
                  >
                    <Merge size={15} />

                    {merging
                      ? "Merging..."
                      : "Confirm merge"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <PersonDetail
          person={selectedPerson}
          onBack={() => {
            setSelectedPerson(null);
            setPersonPhotos([]);
          }}
          onPhotoClick={setSelectedPhoto}
          onPhotosLoaded={setPersonPhotos}
        />
      )}

      {/* -----------------------------------------------------
          PHOTO VIEWER
      ----------------------------------------------------- */}

      <PhotoViewer
        photos={personPhotos}
        selectedPhoto={selectedPhoto}
        onClose={() => setSelectedPhoto(null)}
        onNext={() => {
          if (
            !selectedPhoto ||
            !personPhotos.length
          ) {
            return;
          }

          const index =
            personPhotos.findIndex(
              (photo) =>
                photo.id === selectedPhoto.id
            );

          const nextIndex =
            (index + 1) % personPhotos.length;

          setSelectedPhoto(
            personPhotos[nextIndex]
          );
        }}
        onPrevious={() => {
          if (
            !selectedPhoto ||
            !personPhotos.length
          ) {
            return;
          }

          const index =
            personPhotos.findIndex(
              (photo) =>
                photo.id === selectedPhoto.id
            );

          const previousIndex =
            (index - 1 + personPhotos.length) %
            personPhotos.length;

          setSelectedPhoto(
            personPhotos[previousIndex]
          );
        }}
      />
    </div>
  );
}
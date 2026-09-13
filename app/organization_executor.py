from pathlib import Path

from database import update_photo_path
from vector_store import PhotoVectorStore


def move_photo(item, vector_store=None):
    """
    Safely move one photo and synchronize:

        filesystem
        SQLite
        ChromaDB

    Safety rules:

    - Only SAFE items can be moved.
    - Source must exist.
    - Destination must not exist.
    - Existing files are never overwritten.
    - SQLite is updated only after the file move succeeds.
    - ChromaDB metadata is updated after SQLite.
    - Failures attempt to roll everything back.
    """

    if item["status"] != "SAFE":
        raise ValueError(
            f"Photo {item['photo_id']} is not safe to move: "
            f"{item['status']}"
        )

    source = Path(item["source"])
    destination = Path(item["destination"])

    # Final safety checks.
    if not source.exists():
        raise FileNotFoundError(
            f"Source file does not exist: {source}"
        )

    if destination.exists():
        raise FileExistsError(
            f"Destination already exists: {destination}"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # The current PhotoAgent Images directory and year folders
    # are on the same drive.
    #
    # Path.rename() is used instead of shutil.move() because
    # on Windows it will not silently overwrite an existing file.
    try:
        source.rename(destination)

    except Exception:
        raise

    database_updated = False
    vector_updated = False

    if vector_store is None:
        vector_store = PhotoVectorStore()

    try:

        # ---------------------------------------------------------
        # 1. Update SQLite
        # ---------------------------------------------------------

        update_photo_path(
            item["photo_id"],
            destination,
        )

        database_updated = True

        # ---------------------------------------------------------
        # 2. Update ChromaDB metadata
        # ---------------------------------------------------------

        vector_updated = vector_store.update_photo_path(
            item["photo_id"],
            destination,
        )

        if not vector_updated:
            raise RuntimeError(
                f"Photo {item['photo_id']} does not exist in ChromaDB."
            )

    except Exception as error:

        # ---------------------------------------------------------
        # Roll back ChromaDB
        # ---------------------------------------------------------

        if vector_updated:
            try:
                vector_store.update_photo_path(
                    item["photo_id"],
                    source,
                )

            except Exception as rollback_error:
                raise RuntimeError(
                    "Organization failed and ChromaDB rollback "
                    "also failed."
                ) from rollback_error

        # ---------------------------------------------------------
        # Roll back SQLite
        # ---------------------------------------------------------

        if database_updated:
            try:
                update_photo_path(
                    item["photo_id"],
                    source,
                )

            except Exception as rollback_error:
                raise RuntimeError(
                    "Organization failed and SQLite rollback "
                    "also failed."
                ) from rollback_error

        # ---------------------------------------------------------
        # Roll back physical file
        # ---------------------------------------------------------

        try:

            if destination.exists() and not source.exists():

                source.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                destination.rename(source)

        except Exception as rollback_error:

            raise RuntimeError(
                "Organization failed and physical file rollback "
                "also failed."
            ) from rollback_error

        raise error

    return {
        "photo_id": item["photo_id"],
        "filename": item["filename"],
        "source": str(source),
        "destination": str(destination),
        "status": "MOVED",
    }


def _preflight(plan):
    """
    Validate the entire organization plan before moving anything.

    This is extremely important for batch safety.

    Example:

        photo 1 -> SAFE
        photo 2 -> SAFE
        photo 3 -> CONFLICT

    Result:

        NOTHING gets moved.
    """

    for item in plan:

        if item["status"] == "ALREADY_ORGANIZED":
            continue

        if item["status"] != "SAFE":
            raise ValueError(
                f"Organization aborted: "
                f"{item['filename']} has status "
                f"{item['status']}"
            )

        source = Path(item["source"])
        destination = Path(item["destination"])

        if not source.exists():
            raise FileNotFoundError(
                f"Organization aborted: source missing: "
                f"{source}"
            )

        if destination.exists():
            raise FileExistsError(
                f"Organization aborted: destination already exists: "
                f"{destination}"
            )
            
preflight_plan = _preflight

def execute_plan(plan, confirm=False):
    """
    Execute an organization plan.

    Nothing is moved unless:

        confirm=True

    The complete plan is preflighted before the first file moves.
    """

    if not confirm:
        raise PermissionError(
            "Organization requires explicit confirmation."
        )

    # -------------------------------------------------------------
    # SAFETY CHECK
    # -------------------------------------------------------------

    preflight_plan(plan)

    # One vector-store instance for the entire operation.
    vector_store = PhotoVectorStore()

    results = []

    # -------------------------------------------------------------
    # EXECUTION
    # -------------------------------------------------------------

    for item in plan:

        if item["status"] == "ALREADY_ORGANIZED":

            results.append({
                "photo_id": item["photo_id"],
                "filename": item["filename"],
                "source": item["source"],
                "destination": item["destination"],
                "status": "ALREADY_ORGANIZED",
            })

            continue

        result = move_photo(
            item,
            vector_store=vector_store,
        )

        results.append(result)

    return results
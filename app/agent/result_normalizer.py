from typing import Any, Dict, List


def normalize_photo_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a search result dictionary into the canonical
    photo-result format used by PhotoAgent.

    Canonical format uses:
        id
        filename
        path
    """

    if not isinstance(row, dict):
        raise TypeError("Photo result must be a dictionary.")

    # SearchService currently uses photo_id.
    # Some other components may already use id.
    if "id" in row:
        photo_id = row["id"]
    elif "photo_id" in row:
        photo_id = row["photo_id"]
    else:
        raise ValueError(
            "Photo result is missing both 'id' and 'photo_id'."
        )

    if "filename" not in row:
        raise ValueError(
            "Photo result is missing 'filename'."
        )

    if "path" not in row:
        raise ValueError(
            "Photo result is missing 'path'."
        )

    try:
        photo_id = int(photo_id)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Photo result id must be an integer."
        ) from exc

    normalized = {
        "id": photo_id,
        "filename": str(row["filename"]),
        "path": str(row["path"]),
        "date_taken": row.get("date_taken"),
        "camera": row.get("camera"),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "location_name": row.get("location_name"),
        "similarity": row.get("similarity"),
    }

    return normalized


def normalize_photo_results(
    rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Normalize a list of photo dictionaries.

    Invalid records are skipped rather than crashing the
    entire result set.
    """

    if not isinstance(rows, list):
        raise TypeError("Photo results must be a list.")

    normalized = []
    seen_ids = set()

    for row in rows:
        try:
            photo = normalize_photo_dict(row)
        except (TypeError, ValueError):
            continue

        photo_id = photo["id"]

        if photo_id in seen_ids:
            continue

        seen_ids.add(photo_id)
        normalized.append(photo)

    return normalized
from typing import Iterable, Optional

from photo_result import PhotoResult


def photo_from_dict(data: dict) -> PhotoResult:
    """
    Convert a database/search dictionary into a PhotoResult.
    """

    return PhotoResult(
        id=int(data["id"]),
        filename=data["filename"],
        path=data["path"],
        date_taken=data.get("date_taken"),
        camera=data.get("camera"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        location_name=data.get("location_name"),
        similarity=data.get("similarity"),
    )


def photos_from_dicts(rows: Iterable[dict]) -> list[PhotoResult]:
    """
    Convert multiple dictionaries into PhotoResult objects.
    """

    return [photo_from_dict(row) for row in rows]


def find_photo_by_id(
    photos: Iterable[PhotoResult],
    photo_id: int,
) -> Optional[PhotoResult]:
    """
    Find a PhotoResult by its database ID.
    """

    for photo in photos:
        if photo.id == photo_id:
            return photo

    return None
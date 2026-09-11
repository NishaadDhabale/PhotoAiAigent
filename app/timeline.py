from scanner import scan_photos
from metadata import get_metadata, parse_date_taken


PHOTO_FOLDER = r"D:\project\PhotoAgent\Images"


def build_timeline(folder):
    """Create a chronological list of photos."""

    photos = scan_photos(folder)

    timeline = []

    for photo in photos:
        metadata = get_metadata(photo)

        date_taken = parse_date_taken(
            metadata["date_taken"]
        )

        timeline.append({
            "filename": metadata["filename"],
            "path": metadata["path"],
            "date_taken": date_taken
        })

    # Photos with dates first, sorted chronologically.
    timeline.sort(
        key=lambda photo: (
            photo["date_taken"] is None,
            photo["date_taken"]
        )
    )

    return timeline


if __name__ == "__main__":

    timeline = build_timeline(PHOTO_FOLDER)

    for photo in timeline:
        print(
            photo["date_taken"],
            "->",
            photo["filename"]
        )
from scanner import scan_photos
from metadata import get_metadata, parse_date_taken
from sessions import build_sessions, describe_session
from database import create_database, migrate_database, save_photo
from location import coordinates_to_location
from indexer import index_all_photos

PHOTO_FOLDER = r"D:\project\PhotoAgent\Images"

create_database()
migrate_database()

photos = scan_photos(PHOTO_FOLDER)

print(f"Found {len(photos)} photos\n")

timeline = []

for photo in photos:

    metadata = get_metadata(photo)

    timeline.append({
    "filename": metadata["filename"],
    "path": metadata["path"],
    "date_taken": parse_date_taken(metadata["date_taken"])
    })

    location = None

    if metadata["gps"]:
        location = coordinates_to_location(
            metadata["gps"]["latitude"],
            metadata["gps"]["longitude"]
        )

    save_photo(
        metadata,
        location
    )

    if metadata["gps"]:
        print(f"GPS found: {metadata['gps']}")
        print(f"Location: {location}")

    print(f"Saved: {photo.name}")

timeline.sort(
    key=lambda photo: (
        photo["date_taken"] is None,
        photo["date_taken"]
    )
)

sessions, undated_photos = build_sessions(timeline)

print(f"\nFound {len(sessions)} sessions")

for number, session in enumerate(sessions, start=1):
    information = describe_session(session)

    print(f"\nSession {number}")
    print(f"  Photos: {information['photo_count']}")
    print(f"  Start: {information['start_time']}")
    print(f"  End: {information['end_time']}")
    print(f"  Duration: {information['duration']}")

print(f"\nUndated photos: {len(undated_photos)}")

print("\nUpdating semantic search index...")
index_all_photos()

print("\nDone!")
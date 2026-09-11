from pathlib import Path
from datetime import datetime

from PIL import Image
import exifread


def convert_to_degrees(value):
    """Convert EXIF GPS coordinates to decimal degrees."""
    degrees = float(value.values[0].num) / float(value.values[0].den)
    minutes = float(value.values[1].num) / float(value.values[1].den)
    seconds = float(value.values[2].num) / float(value.values[2].den)

    return degrees + (minutes / 60) + (seconds / 3600)


def extract_gps(tags):
    """Extract latitude and longitude from EXIF tags."""

    latitude = tags.get("GPS GPSLatitude")
    latitude_ref = tags.get("GPS GPSLatitudeRef")

    longitude = tags.get("GPS GPSLongitude")
    longitude_ref = tags.get("GPS GPSLongitudeRef")

    if not all([
        latitude,
        latitude_ref,
        longitude,
        longitude_ref
    ]):
        return None

    lat = convert_to_degrees(latitude)
    lon = convert_to_degrees(longitude)

    if str(latitude_ref) == "S":
        lat = -lat

    if str(longitude_ref) == "W":
        lon = -lon

    return {
        "latitude": lat,
        "longitude": lon
    }

def parse_date_taken(date_string):
    """Convert EXIF date format into a Python datetime."""

    if not date_string:
        return None

    try:
        return datetime.strptime(
            date_string,
            "%Y:%m:%d %H:%M:%S"
        )

    except ValueError:
        return None
    
def get_metadata(photo_path: Path):

    metadata = {
        "filename": photo_path.name,
        "path": str(photo_path),
        "size_bytes": photo_path.stat().st_size,
        "width": None,
        "height": None,
        "date_taken": None,
        "camera": None,
        "gps": None,
    }

    # -------------------------
    # Image dimensions
    # -------------------------

    try:
        with Image.open(photo_path) as image:
            metadata["width"] = image.width
            metadata["height"] = image.height

    except Exception:
        pass

    # -------------------------
    # EXIF metadata
    # -------------------------

    try:
        with open(photo_path, "rb") as file:
            tags = exifread.process_file(
                file,
                details=False
            )

        # Date
        date_taken = tags.get("EXIF DateTimeOriginal")

        if date_taken:
            metadata["date_taken"] = str(date_taken)

        # Camera
        make = tags.get("Image Make")
        model = tags.get("Image Model")

        if make or model:
            metadata["camera"] = " ".join(
                str(value)
                for value in [make, model]
                if value
            )

        # GPS
        metadata["gps"] = extract_gps(tags)

    except Exception:
        pass

    return metadata
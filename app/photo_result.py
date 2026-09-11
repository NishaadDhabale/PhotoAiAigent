from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PhotoResult:
    """
    Normalized representation of a photo returned by PhotoAgent search.
    """

    id: int
    filename: str
    path: str

    date_taken: Optional[str] = None
    camera: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None

    similarity: Optional[float] = None

    def exists(self) -> bool:
        """Return True if the actual photo file exists."""
        return Path(self.path).is_file()

    def path_object(self) -> Path:
        """Return the photo path as a pathlib.Path."""
        return Path(self.path)

    def to_dict(self) -> dict:
        """Convert the result into a normal dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "path": self.path,
            "date_taken": self.date_taken,
            "camera": self.camera,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_name": self.location_name,
            "similarity": self.similarity,
        }
        
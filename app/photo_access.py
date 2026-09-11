import os
import subprocess
import sys
from pathlib import Path

from photo_result import PhotoResult


def validate_photo(photo: PhotoResult) -> Path:
    """
    Validate that a PhotoResult points to an existing local file.
    """

    path = photo.path_object()

    if not path.is_file():
        raise FileNotFoundError(
            f"Photo file does not exist: {path}"
        )

    return path


def open_photo(photo: PhotoResult) -> None:
    """
    Open a photo using the operating system's default image viewer.
    """

    path = validate_photo(photo)

    if sys.platform.startswith("win"):
        os.startfile(str(path))

    elif sys.platform == "darwin":
        subprocess.run(
            ["open", str(path)],
            check=True,
        )

    else:
        subprocess.run(
            ["xdg-open", str(path)],
            check=True,
        )
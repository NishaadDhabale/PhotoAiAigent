from pathlib import Path

from app.database import get_all_photos
from app.photo_access import validate_photo
from app.photo_results import (
    find_photo_by_id,
    photos_from_dicts,
)


def test_conversion():
    print("=" * 60)
    print("PhotoResult Test Suite")
    print("=" * 60)

    print("\nTest 1: Database → PhotoResult")

    rows = get_all_photos()

    assert rows
    assert len(rows) == 27

    photos = photos_from_dicts(rows)

    assert len(photos) == 27

    for photo in photos:
        assert isinstance(photo.id, int)
        assert photo.filename
        assert photo.path

    print(f"Converted {len(photos)} photos: OK")


def test_file_existence(photos):
    print("\nTest 2: Actual photo files")

    existing = 0
    missing = []

    for photo in photos:
        if photo.exists():
            existing += 1
        else:
            missing.append(photo.path)

    print(f"Existing files: {existing}/{len(photos)}")

    if missing:
        print("\nMissing files:")
        for path in missing:
            print(path)

    assert existing == len(photos)

    print("All photo files exist: OK")


def test_lookup(photos):
    print("\nTest 3: Photo lookup by ID")

    first = photos[0]

    result = find_photo_by_id(
        photos,
        first.id,
    )

    assert result is not None
    assert result.id == first.id
    assert result.filename == first.filename
    assert result.path == first.path

    missing = find_photo_by_id(
        photos,
        -999999,
    )

    assert missing is None

    print("Photo lookup: OK")


def test_path_validation(photos):
    print("\nTest 4: Path validation")

    for photo in photos[:5]:
        path = validate_photo(photo)

        assert isinstance(path, Path)
        assert path.is_file()

    print("Path validation: OK")


def test_serialization(photos):
    print("\nTest 5: PhotoResult serialization")

    photo = photos[0]

    data = photo.to_dict()

    assert isinstance(data, dict)
    assert data["id"] == photo.id
    assert data["filename"] == photo.filename
    assert data["path"] == photo.path

    print("Serialization: OK")


def main():
    rows = get_all_photos()
    photos = photos_from_dicts(rows)

    test_conversion()
    test_file_existence(photos)
    test_lookup(photos)
    test_path_validation(photos)
    test_serialization(photos)

    print("\n" + "=" * 60)
    print("ALL PHOTO RESULT TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
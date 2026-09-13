from pathlib import Path
from unittest.mock import patch

from app.organization_planner import plan_by_year


def make_photo(photo_id, filename, date_taken):
    return {
        "id": photo_id,
        "filename": filename,
        "path": rf"D:\project\PhotoAgent\Images\{filename}",
        "date_taken": date_taken,
        "camera": None,
        "location_name": None,
    }


FAKE_PHOTOS = [
    make_photo(
        1,
        "photo2022.jpg",
        "2022:01:24 21:32:35",
    ),
    make_photo(
        2,
        "photo2023.jpg",
        "2023:07:22 20:47:08",
    ),
    make_photo(
        3,
        "undated.jpg",
        None,
    ),
]


def test_safe_photo():
    photo = FAKE_PHOTOS[0]
    source = Path(photo["path"])

    def fake_exists(path):
        return path == source

    with patch(
        "organization_planner.get_all_photos",
        return_value=[photo],
    ), patch.object(Path, "exists", fake_exists):
        plan = plan_by_year()

    assert plan[0]["status"] == "SAFE"


def test_conflict_detection():
    photo = FAKE_PHOTOS[0]

    source = Path(photo["path"])
    destination = source.parent / "2022" / source.name

    def fake_exists(path):
        return path == source or path == destination

    with patch(
        "organization_planner.get_all_photos",
        return_value=[photo],
    ), patch.object(Path, "exists", fake_exists):
        plan = plan_by_year()

    assert plan[0]["status"] == "CONFLICT"


def test_already_organized():
    photo = make_photo(
        4,
        "already.jpg",
        "2022:01:24 21:32:35",
    )

    # The photo is already inside its 2022 directory.
    photo["path"] = (
        r"D:\project\PhotoAgent\Images\2022\already.jpg"
    )

    source = Path(photo["path"])

    with patch(
        "organization_planner.get_all_photos",
        return_value=[photo],
    ), patch.object(Path, "exists", return_value=True):
        plan = plan_by_year()

    assert plan[0]["source"] == str(source)
    assert plan[0]["destination"] == str(source)
    assert plan[0]["status"] == "ALREADY_ORGANIZED"

def test_missing_source():
    photo = FAKE_PHOTOS[0]

    with patch(
        "organization_planner.get_all_photos",
        return_value=[photo],
    ), patch.object(Path, "exists", return_value=False):
        plan = plan_by_year()

    assert plan[0]["status"] == "MISSING_SOURCE"


def test_undated_photo():
    photo = FAKE_PHOTOS[2]
    source = Path(photo["path"])

    def fake_exists(path):
        return path == source

    with patch(
        "organization_planner.get_all_photos",
        return_value=[photo],
    ), patch.object(Path, "exists", fake_exists):
        plan = plan_by_year()

    assert plan[0]["year"] == "Undated"
    assert plan[0]["status"] == "SAFE"


if __name__ == "__main__":
    test_safe_photo()
    test_conflict_detection()
    test_already_organized()
    test_missing_source()
    test_undated_photo()

    print("✓ Safe photo detection")
    print("✓ Conflict detection")
    print("✓ Already-organized detection")
    print("✓ Missing-source detection")
    print("✓ Undated handling")
    print("ALL ORGANIZATION SAFETY TESTS PASSED")
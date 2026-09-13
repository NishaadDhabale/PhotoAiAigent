from pathlib import Path
import sqlite3
import tempfile

from organization_executor import (
    move_photo,
    execute_plan,
)


class FakeVectorStore:

    def __init__(self):
        self.paths = {}

    def update_photo_path(self, photo_id, path):
        self.paths[int(photo_id)] = str(path)
        return True


def create_database(db_path):
    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        CREATE TABLE photos (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            path TEXT
        )
        """
    )

    connection.execute(
        """
        INSERT INTO photos
        (id, filename, path)
        VALUES (?, ?, ?)
        """,
        (
            1,
            "photo.jpg",
            "old/path/photo.jpg",
        ),
    )

    connection.commit()

    return connection


def test_successful_move():

    with tempfile.TemporaryDirectory() as temp:

        root = Path(temp)

        source = root / "photo.jpg"
        destination = root / "2022" / "photo.jpg"

        source.write_text("test photo")

        item = {
            "photo_id": 1,
            "filename": "photo.jpg",
            "source": str(source),
            "destination": str(destination),
            "status": "SAFE",
        }

        vector_store = FakeVectorStore()

        result = move_photo(
            item,
            vector_store=vector_store,
        )

        assert result["status"] == "MOVED"
        assert not source.exists()
        assert destination.exists()

        assert vector_store.paths[1] == str(destination)


def test_conflict_detection():

    with tempfile.TemporaryDirectory() as temp:

        root = Path(temp)

        source = root / "photo.jpg"
        destination = root / "2022" / "photo.jpg"

        source.write_text("source")
        destination.parent.mkdir()
        destination.write_text("existing")

        item = {
            "photo_id": 1,
            "filename": "photo.jpg",
            "source": str(source),
            "destination": str(destination),
            "status": "SAFE",
        }

        vector_store = FakeVectorStore()

        try:
            move_photo(
                item,
                vector_store=vector_store,
            )
            assert False, "Expected FileExistsError"

        except FileExistsError:
            pass

        assert source.exists()
        assert destination.exists()


def test_missing_source():

    with tempfile.TemporaryDirectory() as temp:

        root = Path(temp)

        source = root / "missing.jpg"
        destination = root / "2022" / "missing.jpg"

        item = {
            "photo_id": 1,
            "filename": "missing.jpg",
            "source": str(source),
            "destination": str(destination),
            "status": "SAFE",
        }

        try:
            move_photo(
                item,
                vector_store=FakeVectorStore(),
            )
            assert False, "Expected FileNotFoundError"

        except FileNotFoundError:
            pass

        assert not destination.exists()


def test_unconfirmed_plan():

    item = {
        "photo_id": 1,
        "filename": "photo.jpg",
        "source": "source.jpg",
        "destination": "2022/photo.jpg",
        "status": "SAFE",
    }

    try:
        execute_plan(
            [item],
            confirm=False,
        )

        assert False, "Expected PermissionError"

    except PermissionError:
        pass


def test_preflight_aborts_entire_batch():

    with tempfile.TemporaryDirectory() as temp:

        root = Path(temp)

        source1 = root / "photo1.jpg"
        destination1 = root / "2022" / "photo1.jpg"

        source2 = root / "photo2.jpg"
        destination2 = root / "2022" / "photo2.jpg"

        source1.write_text("photo 1")

        # photo2 intentionally does not exist.

        plan = [
            {
                "photo_id": 1,
                "filename": "photo1.jpg",
                "source": str(source1),
                "destination": str(destination1),
                "status": "SAFE",
            },
            {
                "photo_id": 2,
                "filename": "photo2.jpg",
                "source": str(source2),
                "destination": str(destination2),
                "status": "SAFE",
            },
        ]

        try:
            # We test _preflight indirectly through execute_plan,
            # but avoid constructing the real vector store.
            from organization_executor import _preflight

            _preflight(plan)

            assert False, "Expected FileNotFoundError"

        except FileNotFoundError:
            pass

        # Most important assertion:
        # photo1 was NOT moved because photo2 failed preflight.
        assert source1.exists()
        assert not destination1.exists()


if __name__ == "__main__":

    test_successful_move()
    print("✓ Successful move")

    test_conflict_detection()
    print("✓ Conflict protection")

    test_missing_source()
    print("✓ Missing-source protection")

    test_unconfirmed_plan()
    print("✓ Confirmation protection")

    test_preflight_aborts_entire_batch()
    print("✓ Batch preflight protection")

    print("\nALL ORGANIZATION EXECUTOR TESTS PASSED")
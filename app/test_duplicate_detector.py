import tempfile
from pathlib import Path

import numpy as np

from duplicate_detector import (
    cosine_similarity,
    file_hash,
    find_exact_duplicates,
)

from duplicate_detector import find_near_duplicates


class FakeEmbedder:
    def __init__(self):
        self.embeddings = {}

    def embed_image(self, path):
        path = str(path)

        return self.embeddings[path]

def test_near_duplicate_detection():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)

        first = directory / "first.jpg"
        second = directory / "second.jpg"
        third = directory / "third.jpg"

        first.write_bytes(b"first")
        second.write_bytes(b"second")
        third.write_bytes(b"third")

        photos = [
            make_photo(1, first),
            make_photo(2, second),
            make_photo(3, third),
        ]

        embedder = FakeEmbedder()

        embedder.embeddings[str(first)] = np.array(
            [1.0, 0.0, 0.0],
            dtype=np.float32,
        )

        embedder.embeddings[str(second)] = np.array(
            [0.99, 0.01, 0.0],
            dtype=np.float32,
        )

        embedder.embeddings[str(third)] = np.array(
            [0.0, 1.0, 0.0],
            dtype=np.float32,
        )

        matches = find_near_duplicates(
            photos,
            threshold=0.9,
            embedder=embedder,
        )

        assert len(matches) == 1

        assert {
            matches[0]["photo_a"]["id"],
            matches[0]["photo_b"]["id"],
        } == {1, 2}

        assert matches[0]["similarity"] >= 0.9

        print("✓ Near-duplicate detection")

def make_photo(
    photo_id,
    path,
):
    return {
        "id": photo_id,
        "path": str(path),
        "filename": Path(path).name,
    }


def test_file_hash_same_content():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)

        first = directory / "first.txt"
        second = directory / "second.txt"

        first.write_bytes(b"PhotoAgent duplicate test")
        second.write_bytes(b"PhotoAgent duplicate test")

        assert file_hash(first) == file_hash(second)

        print("✓ Same files have same hash")


def test_file_hash_different_content():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)

        first = directory / "first.txt"
        second = directory / "second.txt"

        first.write_bytes(b"photo one")
        second.write_bytes(b"photo two")

        assert file_hash(first) != file_hash(second)

        print("✓ Different files have different hashes")


def test_exact_duplicate_groups():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)

        first = directory / "first.jpg"
        second = directory / "second.jpg"
        third = directory / "third.jpg"

        first.write_bytes(b"same image")
        second.write_bytes(b"same image")
        third.write_bytes(b"different image")

        photos = [
            make_photo(1, first),
            make_photo(2, second),
            make_photo(3, third),
        ]

        groups = find_exact_duplicates(photos)

        assert len(groups) == 1
        assert len(groups[0]) == 2

        ids = {
            photo["id"]
            for photo in groups[0]
        }

        assert ids == {1, 2}

        print("✓ Exact duplicate grouping")


def test_no_exact_duplicates():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)

        first = directory / "first.jpg"
        second = directory / "second.jpg"

        first.write_bytes(b"image one")
        second.write_bytes(b"image two")

        photos = [
            make_photo(1, first),
            make_photo(2, second),
        ]

        groups = find_exact_duplicates(photos)

        assert groups == []

        print("✓ No false exact duplicates")


def test_cosine_identical_vectors():
    vector = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    similarity = cosine_similarity(
        vector,
        vector,
    )

    assert abs(similarity - 1.0) < 1e-6

    print("✓ Identical vectors similarity = 1")


def test_cosine_orthogonal_vectors():
    first = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    second = np.array(
        [0.0, 1.0, 0.0],
        dtype=np.float32,
    )

    similarity = cosine_similarity(
        first,
        second,
    )

    assert abs(similarity) < 1e-6

    print("✓ Orthogonal vectors similarity = 0")


def test_cosine_zero_vector():
    first = np.array(
        [0.0, 0.0, 0.0],
        dtype=np.float32,
    )

    second = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    assert cosine_similarity(
        first,
        second,
    ) == 0.0

    print("✓ Zero-vector handling")


if __name__ == "__main__":
    test_file_hash_same_content()
    test_file_hash_different_content()
    test_exact_duplicate_groups()
    test_no_exact_duplicates()
    test_cosine_identical_vectors()
    test_cosine_orthogonal_vectors()
    test_cosine_zero_vector()
    test_near_duplicate_detection()

    print()
    print("ALL DUPLICATE DETECTOR TESTS PASSED")
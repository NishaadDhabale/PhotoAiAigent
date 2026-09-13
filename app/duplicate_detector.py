from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

from image_embeddings import ImageEmbedder


DEFAULT_SIMILARITY_THRESHOLD = 0.92


def file_hash(
    path: str | Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Calculate a SHA-256 hash for a local file.
    """

    digest = hashlib.sha256()

    with Path(path).open("rb") as file:
        while True:
            chunk = file.read(chunk_size)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def find_exact_duplicates(
    photos: Iterable[dict],
) -> list[list[dict]]:
    """
    Find files whose contents are byte-for-byte identical.

    Returns only groups containing two or more photos.
    """

    groups = defaultdict(list)

    for photo in photos:
        path = Path(photo["path"])

        if not path.is_file():
            continue

        digest = file_hash(path)
        groups[digest].append(photo)

    return [
        group
        for group in groups.values()
        if len(group) > 1
    ]


def cosine_similarity(
    embedding_a: np.ndarray,
    embedding_b: np.ndarray,
) -> float:
    """
    Calculate cosine similarity between two embeddings.
    """

    a = np.asarray(
        embedding_a,
        dtype=np.float32,
    )

    b = np.asarray(
        embedding_b,
        dtype=np.float32,
    )

    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)

    if a_norm == 0 or b_norm == 0:
        return 0.0

    return float(
        np.dot(a, b)
        / (a_norm * b_norm)
    )


def find_near_duplicates(
    photos: Iterable[dict],
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    embedder: ImageEmbedder | None = None,
) -> list[dict]:
    """
    Find visually similar photo pairs.

    Uses the project's existing ImageEmbedder.

    This function never modifies or deletes files.
    """

    photos = list(photos)

    if embedder is None:
        embedder = ImageEmbedder()

    embedded_photos = []

    for photo in photos:
        path = Path(photo["path"])

        if not path.is_file():
            continue

        embedding = embedder.embed_image(path)

        embedded_photos.append(
            {
                "photo": photo,
                "embedding": np.asarray(
                    embedding,
                    dtype=np.float32,
                ),
            }
        )

    matches = []

    for i in range(len(embedded_photos)):
        for j in range(
            i + 1,
            len(embedded_photos),
        ):
            first = embedded_photos[i]
            second = embedded_photos[j]

            similarity = cosine_similarity(
                first["embedding"],
                second["embedding"],
            )

            if similarity >= threshold:
                matches.append(
                    {
                        "photo_a": first["photo"],
                        "photo_b": second["photo"],
                        "similarity": similarity,
                    }
                )

    matches.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return matches
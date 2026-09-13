from pathlib import Path

import numpy as np

from app.image_embeddings import (
    ImageEmbedder,
    cosine_similarity,
)


IMAGE_DIR = Path(
    r"D:\project\PhotoAgent\Images"
)


def main():
    image_paths = sorted(
        path
        for path in IMAGE_DIR.iterdir()
        if path.suffix.lower()
        in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".heic",
            ".heif",
        }
    )

    assert image_paths, "No images found"

    print(
        f"Found {len(image_paths)} images"
    )

    embedder = ImageEmbedder()

    # ----------------------------------------
    # Image embedding
    # ----------------------------------------

    image_a = embedder.embed_image(
        image_paths[0]
    )

    image_b = embedder.embed_image(
        image_paths[1]
    )

    print(
        f"Image embedding dimension: "
        f"{image_a.shape[0]}"
    )

    print(
        f"Image dtype: {image_a.dtype}"
    )

    print(
        f"Image A norm: "
        f"{np.linalg.norm(image_a):.4f}"
    )

    assert image_a.ndim == 1
    assert image_a.dtype == np.float32
    assert image_a.shape == image_b.shape

    assert np.isclose(
        np.linalg.norm(image_a),
        1.0,
        atol=1e-3,
    )

    # ----------------------------------------
    # Text embedding
    # ----------------------------------------

    text_embedding = embedder.embed_text(
        "a photo of a person"
    )

    print(
        f"Text embedding dimension: "
        f"{text_embedding.shape[0]}"
    )

    print(
        f"Text norm: "
        f"{np.linalg.norm(text_embedding):.4f}"
    )

    assert text_embedding.ndim == 1
    assert text_embedding.dtype == np.float32
    assert text_embedding.shape == image_a.shape

    assert np.isclose(
        np.linalg.norm(text_embedding),
        1.0,
        atol=1e-3,
    )

    # ----------------------------------------
    # Cross-modal similarity
    # ----------------------------------------

    similarity = cosine_similarity(
        image_a,
        text_embedding,
    )

    print(
        f"Image ↔ text similarity: "
        f"{similarity:.4f}"
    )

    assert -1.0 <= similarity <= 1.0

    # ----------------------------------------
    # Different images should not be identical
    # ----------------------------------------

    image_similarity = cosine_similarity(
        image_a,
        image_b,
    )

    print(
        f"Image A ↔ Image B similarity: "
        f"{image_similarity:.4f}"
    )

    assert not np.array_equal(
        image_a,
        image_b,
    )

    print()
    print(
        "Image embedding tests passed."
    )


if __name__ == "__main__":
    main()
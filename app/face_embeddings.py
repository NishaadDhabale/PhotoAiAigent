import cv2
import numpy as np

from insightface.app import FaceAnalysis


class FaceEmbedder:

    def embed(self, detected_face):
        embedding = detected_face.get("embedding")

        if embedding is None:
            raise ValueError(
                "Detected face does not contain an embedding."
            )

        return np.asarray(
            embedding,
            dtype=np.float32,
        )

def cosine_similarity(embedding_a, embedding_b):
    vector_a = np.asarray(
        embedding_a,
        dtype=np.float32,
    )

    vector_b = np.asarray(
        embedding_b,
        dtype=np.float32,
    )

    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(vector_a, vector_b)
        / denominator
    )


if __name__ == "__main__":
    from pathlib import Path

    from face_detection import detect_faces

    test_photo = Path(
        r"D:\project\PhotoAgent\Images\IMG_20230722_204708.jpg"
    )

    print("Detecting faces...")

    detected_faces = detect_faces(test_photo)

    print(
        "Detected faces:",
        len(detected_faces),
    )

    if not detected_faces:
        raise RuntimeError(
            "No faces detected in test photo."
        )

    embedder = FaceEmbedder()

    embedding = embedder.embed(
        detected_faces[0]
    )

    print(
        "Embedding shape:",
        embedding.shape,
    )

    print(
        "Embedding dtype:",
        embedding.dtype,
    )

    print(
        "Embedding norm:",
        np.linalg.norm(embedding),
    )
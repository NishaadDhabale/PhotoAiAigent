import numpy as np
from sklearn.cluster import AgglomerativeClustering

DEFAULT_DISTANCE_THRESHOLD = 0.40


def normalize_embedding(embedding):
    vector = np.asarray(embedding, dtype=np.float32)
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def cluster_faces(face_records, distance_threshold=DEFAULT_DISTANCE_THRESHOLD):
    """
    Group faces using cosine distance.

    Cosine distance = 1 - cosine similarity.

    For example:
        similarity 0.60 -> distance 0.40
        similarity 0.80 -> distance 0.20
    """

    if not face_records:
        return []

    embeddings = np.asarray(
        [
            normalize_embedding(face["embedding"])
            for face in face_records
        ],
        dtype=np.float32,
    )

    # One face cannot be clustered with anything else.
    if len(face_records) == 1:
        face_records[0]["person_group_id"] = 0

        return [
            {
                "faces": [face_records[0]],
                "representative_embedding": embeddings[0],
            }
        ]

    clustering = AgglomerativeClustering(
        n_clusters=None,
        metric="cosine",
        linkage="average",
        distance_threshold=distance_threshold,
    )

    labels = clustering.fit_predict(embeddings)

    groups = []

    for group_id in sorted(set(labels)):
        group_faces = [
            face_records[index]
            for index, label in enumerate(labels)
            if label == group_id
        ]

        group_embeddings = embeddings[
            [index for index, label in enumerate(labels) if label == group_id]
        ]

        centroid = np.mean(group_embeddings, axis=0)
        representative_embedding = normalize_embedding(centroid)

        for face in group_faces:
            face["person_group_id"] = int(group_id)

        groups.append(
            {
                "faces": group_faces,
                "representative_embedding": representative_embedding,
            }
        )

    return groups


# Keep the old function name temporarily so existing code does not break.
def group_faces(face_records, threshold=0.60):
    """
    Compatibility wrapper.

    The old API used similarity threshold.
    The new clustering API uses cosine distance.

    similarity >= 0.60
    corresponds approximately to
    distance <= 0.40.
    """

    distance_threshold = 1.0 - threshold

    return cluster_faces(
        face_records,
        distance_threshold=distance_threshold,
    )
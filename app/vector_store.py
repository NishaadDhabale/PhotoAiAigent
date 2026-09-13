from pathlib import Path

import numpy as np
import chromadb
from chromadb.config import Settings


VECTOR_DB_PATH = Path(r"D:\project\PhotoAgent\data\chroma")
COLLECTION_NAME = "photo_embeddings"


class PhotoVectorStore:
    def __init__(
        self,
        db_path=VECTOR_DB_PATH,
        collection_name=COLLECTION_NAME,
    ):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
            ),
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": "MobileCLIP2-S0",
                "embedding_pretrained": "dfndr2b",
                "embedding_dimension": 512,
            },
        )

    def count(self):
        """Return the number of stored photo embeddings."""
        return self.collection.count()

    def has_photo(self, photo_id):
        """Return True if a photo embedding already exists in ChromaDB."""

        result = self.collection.get(
            ids=[str(photo_id)],
            include=[],
        )

        return bool(result["ids"])

    def upsert_photo(
        self,
        photo_id,
        embedding,
        filename=None,
        path=None,
        date_taken=None,
        location_name=None,
        camera=None,
    ):
        """Insert or update one photo embedding."""

        metadata = {
            "photo_id": int(photo_id),
        }

        if filename is not None:
            metadata["filename"] = str(filename)

        if path is not None:
            metadata["path"] = str(path)

        if date_taken is not None:
            metadata["date_taken"] = str(date_taken)

        if location_name is not None:
            metadata["location_name"] = str(location_name)

        if camera is not None:
            metadata["camera"] = str(camera)

        self.collection.upsert(
            ids=[str(photo_id)],
            embeddings=[embedding.tolist()],
            metadatas=[metadata],
        )

    def upsert_photos(self, photos):
        """
        Insert or update multiple photo embeddings.

        Each item in photos should contain:
            photo_id
            embedding

        Optional:
            filename
            path
            date_taken
            location_name
            camera
        """

        if not photos:
            return

        ids = []
        embeddings = []
        metadatas = []

        for photo in photos:
            photo_id = int(photo["photo_id"])

            metadata = {
                "photo_id": photo_id,
            }

            optional_fields = [
                "filename",
                "path",
                "date_taken",
                "location_name",
                "camera",
            ]

            for field in optional_fields:
                value = photo.get(field)

                if value is not None:
                    metadata[field] = str(value)

            ids.append(str(photo_id))
            embeddings.append(photo["embedding"].tolist())
            metadatas.append(metadata)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search_by_embedding(self, embedding, n_results=5):
        """Find photos most similar to an embedding."""

        if self.count() == 0:
            return []

        n_results = min(n_results, self.count())

        results = self.collection.query(
            query_embeddings=[
              np.asarray(embedding, dtype=np.float32).tolist()
            ],
            n_results=n_results,
            include=[
                "metadatas",
                "distances",
            ],
        )

        matches = []

        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for photo_id, metadata, distance in zip(
            ids,
            metadatas,
            distances,
        ):
            matches.append(
                {
                    "photo_id": int(photo_id),
                    "metadata": metadata,
                    "distance": float(distance),
                    "similarity": 1.0 - float(distance),
                }
            )

        return matches

    def get_photo(self, photo_id):
        """Retrieve one stored photo embedding and metadata."""

        result = self.collection.get(
            ids=[str(photo_id)],
            include=[
                "embeddings",
                "metadatas",
            ],
        )

        if not result["ids"]:
            return None

        return {
            "photo_id": int(result["ids"][0]),
            "embedding": result["embeddings"][0],
            "metadata": result["metadatas"][0],
        }

    def update_photo_path(self, photo_id, path):
        """
        Update only the stored filesystem path for an existing photo.

        The embedding itself is not changed.
        """

        photo_id = str(photo_id)

        result = self.collection.get(
            ids=[photo_id],
            include=["metadatas"],
        )

        if not result["ids"]:
            return False

        metadata = result["metadatas"][0] or {}

        metadata["path"] = str(path)

        self.collection.update(
            ids=[photo_id],
            metadatas=[metadata],
        )

        return True
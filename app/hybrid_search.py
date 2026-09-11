from database import get_all_photos, get_photos_by_ids
from search import search_photos
from semantic_search import SemanticPhotoSearch


class HybridPhotoSearch:
    """
    Combines structured SQLite filtering with semantic search.

    Structured filters determine which photos are eligible.
    Semantic similarity ranks those eligible photos.
    """

    def __init__(self, semantic_searcher=None):
      self.semantic_searcher = (
          semantic_searcher
          if semantic_searcher is not None
          else SemanticPhotoSearch()
    )

    def search(
        self,
        semantic_query=None,
        person=None,
        year=None,
        start_date=None,
        end_date=None,
        location=None,
        camera=None,
        filename=None,
        n_results=10,
    ):
        """
        Perform a hybrid search.

        Structured filters are applied first when provided.
        Semantic similarity is then used to rank the eligible photos.
        """

        if n_results <= 0:
            raise ValueError("n_results must be greater than zero")

        has_structured_filters = any(
            value is not None
            for value in [
                person,
                year,
                start_date,
                end_date,
                location,
                camera,
                filename,
            ]
        )

        # =====================================================
        # STRUCTURED-ONLY SEARCH
        # =====================================================

        if semantic_query is None or not semantic_query.strip():

            if has_structured_filters:
                photos = search_photos(
                    person=person,
                    year=year,
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    camera=camera,
                    filename=filename,
                )

            else:
                photos = get_all_photos()

            return [
                {
                    "photo_id": photo["photo_id"]
                    if "photo_id" in photo
                    else photo["id"],
                    "filename": photo["filename"],
                    "path": photo["path"],
                    "date_taken": photo["date_taken"],
                    "location_name": photo["location_name"],
                    "camera": photo["camera"],
                    "similarity": None,
                }
                for photo in photos[:n_results]
            ]

        # =====================================================
        # SEMANTIC SEARCH
        # =====================================================

        semantic_results = self.semantic_searcher.search(
            semantic_query,
            n_results=self.semantic_searcher.store.count(),
        )

        if not semantic_results:
            return []

        # =====================================================
        # APPLY STRUCTURED FILTERS
        # =====================================================

        if has_structured_filters:

            structured_results = search_photos(
                person=person,
                year=year,
                start_date=start_date,
                end_date=end_date,
                location=location,
                camera=camera,
                filename=filename,
            )

            allowed_ids = {
                int(photo["photo_id"])
                for photo in structured_results
            }

            semantic_results = [
                result
                for result in semantic_results
                if result["photo_id"] in allowed_ids
            ]

        if not semantic_results:
            return []

        # =====================================================
        # GET FULL METADATA FROM SQLITE
        # =====================================================

        photo_ids = [
            result["photo_id"]
            for result in semantic_results
        ]

        photos = get_photos_by_ids(photo_ids)

        photos_by_id = {
            photo["id"]: photo
            for photo in photos
        }

        # =====================================================
        # COMBINE RESULTS
        # =====================================================

        final_results = []

        for result in semantic_results:

            photo_id = result["photo_id"]

            photo = photos_by_id.get(photo_id)

            if photo is None:
                continue

            final_results.append(
                {
                    "photo_id": photo_id,
                    "filename": photo["filename"],
                    "path": photo["path"],
                    "date_taken": photo["date_taken"],
                    "location_name": photo["location_name"],
                    "camera": photo["camera"],
                    "similarity": result["similarity"],
                }
            )

        return final_results[:n_results]


def hybrid_search(
    semantic_query=None,
    person=None,
    year=None,
    start_date=None,
    end_date=None,
    location=None,
    camera=None,
    filename=None,
    n_results=10,
):
    """
    Convenience function for one-off hybrid searches.
    """

    searcher = HybridPhotoSearch()

    return searcher.search(
        semantic_query=semantic_query,
        person=person,
        year=year,
        start_date=start_date,
        end_date=end_date,
        location=location,
        camera=camera,
        filename=filename,
        n_results=n_results,
    )


if __name__ == "__main__":

    print("=" * 70)
    print("PhotoAgent Hybrid Search")
    print("=" * 70)

    searcher = HybridPhotoSearch()

    results = searcher.search(
        semantic_query="a photo of a person",
        n_results=10,
    )

    print()
    print('Query: "a photo of a person"')
    print()

    for index, result in enumerate(results, start=1):

        print(
            f"{index:2}. "
            f"similarity={result['similarity']:.4f} "
            f"photo_id={result['photo_id']} "
            f"filename={result['filename']}"
        )
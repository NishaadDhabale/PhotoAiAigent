from hybrid_search import HybridPhotoSearch
from search import search_photos
from semantic_search import SemanticPhotoSearch


class PhotoSearchService:
    """
    High-level search service used by the future AI agent.
    """

    def __init__(self):
        # Create one semantic searcher.
        self.semantic_searcher = SemanticPhotoSearch()

        # Reuse the same semantic searcher inside hybrid search.
        self.hybrid_searcher = HybridPhotoSearch(
            semantic_searcher=self.semantic_searcher
        )

    def structured_search(
        self,
        person=None,
        year=None,
        start_date=None,
        end_date=None,
        location=None,
        camera=None,
        filename=None,
    ):
        return search_photos(
            person=person,
            year=year,
            start_date=start_date,
            end_date=end_date,
            location=location,
            camera=camera,
            filename=filename,
        )

    def semantic_search(
        self,
        query,
        n_results=10,
    ):
        return self.semantic_searcher.search(
            query=query,
            n_results=n_results,
        )

    def hybrid_search(
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
        return self.hybrid_searcher.search(
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


def structured_photo_search(
    person=None,
    year=None,
    start_date=None,
    end_date=None,
    location=None,
    camera=None,
    filename=None,
):
    service = PhotoSearchService()

    return service.structured_search(
        person=person,
        year=year,
        start_date=start_date,
        end_date=end_date,
        location=location,
        camera=camera,
        filename=filename,
    )


def semantic_photo_search(
    query,
    n_results=10,
):
    service = PhotoSearchService()

    return service.semantic_search(
        query=query,
        n_results=n_results,
    )


def hybrid_photo_search(
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
    service = PhotoSearchService()

    return service.hybrid_search(
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
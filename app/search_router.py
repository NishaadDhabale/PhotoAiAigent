from query_parser import parse_query
from search_service import PhotoSearchService


class SearchRouter:
    """
    Routes interpreted queries to the correct existing search mechanism.

    Structured-only:
        SQLite

    Semantic-only:
        Chroma / MobileCLIP

    Structured + semantic:
        Hybrid search
    """

    def __init__(self, search_service=None):
        self.search_service = search_service or PhotoSearchService()

    def search(self, query: str, n_results: int = 10):
        parsed = parse_query(query)

        # ---------------------------------------------------------
        # EMPTY QUERY
        # ---------------------------------------------------------
        if not parsed.has_structured_filters and not parsed.has_semantic_query:
            return self.search_service.structured_search()[:n_results]

        structured_kwargs = {
            "person": parsed.person,
            "year": parsed.year,
            "start_date": parsed.start_date,
            "end_date": parsed.end_date,
            "location": parsed.location,
            "camera": parsed.camera,
            "filename": parsed.filename,
        }

        # ---------------------------------------------------------
        # STRUCTURED + SEMANTIC
        # ---------------------------------------------------------
        if parsed.has_structured_filters and parsed.has_semantic_query:
            return self.search_service.hybrid_search(
                semantic_query=parsed.semantic_query,
                n_results=n_results,
                **structured_kwargs,
            )

        # ---------------------------------------------------------
        # STRUCTURED ONLY
        # ---------------------------------------------------------
        if parsed.has_structured_filters:
            return self.search_service.structured_search(
                **structured_kwargs
            )[:n_results]

        # ---------------------------------------------------------
        # SEMANTIC ONLY
        # ---------------------------------------------------------
        return self.search_service.semantic_search(
            parsed.semantic_query,
            n_results,
        )
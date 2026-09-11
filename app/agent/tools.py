import json
from typing import Optional

from langchain_core.tools import StructuredTool

from search_service import PhotoSearchService
from agent.result_normalizer import normalize_photo_results
# Create one shared search service instance.
_search_service = PhotoSearchService()


def _serialize_results(results) -> str:
    """
    Convert search results into the canonical JSON response
    expected by the agent and CLI.
    """

    normalized = normalize_photo_results(results)

    return json.dumps(
        {
            "count": len(normalized),
            "results": normalized,
        },
        ensure_ascii=False,
        default=str,
    )

def _error_response(message: str) -> str:
    """
    Return a consistent JSON error response.
    """
    return json.dumps(
        {
            "count": 0,
            "results": [],
            "error": message,
        },
        ensure_ascii=False,
    )


def structured_photo_search_tool(
    person: Optional[str] = None,
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
    camera: Optional[str] = None,
    filename: Optional[str] = None,
) -> str:
    """
    Search photos using exact structured metadata filters.

    Use this tool when the user specifies metadata constraints
    such as a person, year, date range, location, camera, or
    filename.

    Do not use this tool for visual concepts such as beaches,
    sunsets, food, cars, or outdoor scenes unless those concepts
    are represented by metadata filters.
    """
    try:
        results = _search_service.structured_search(
            person=person,
            year=year,
            start_date=start_date,
            end_date=end_date,
            location=location,
            camera=camera,
            filename=filename,
        )

        return _serialize_results(results)

    except Exception as exc:
        return _error_response(
            f"Structured photo search failed: {exc}"
        )


def semantic_photo_search_tool(
    query: str,
    n_results: int = 10,
) -> str:
    """
    Search photos using natural-language semantic similarity.

    Use this tool for visual or conceptual requests such as:
    beaches, sunsets, food, cars, buildings, outdoor scenes,
    people, animals, celebrations, or similar concepts.

    Do not use this tool when the request only contains exact
    metadata filters such as a specific year or filename.
    """
    if not isinstance(query, str) or not query.strip():
        return _error_response(
            "Semantic search requires a non-empty query."
        )

    if not isinstance(n_results, int):
        return _error_response(
            "n_results must be an integer."
        )

    if n_results < 1:
        return _error_response(
            "n_results must be at least 1."
        )

    if n_results > 100:
        return _error_response(
            "n_results cannot exceed 100."
        )

    try:
        results = _search_service.semantic_search(
            query=query.strip(),
            n_results=n_results,
        )

        return _serialize_results(results)

    except Exception as exc:
        return _error_response(
            f"Semantic photo search failed: {exc}"
        )


def hybrid_photo_search_tool(
    semantic_query: Optional[str] = None,
    person: Optional[str] = None,
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
    camera: Optional[str] = None,
    filename: Optional[str] = None,
    n_results: int = 10,
) -> str:
    """
    Search photos using both structured metadata filters and
    semantic similarity.

    Use this when the user's request combines metadata constraints
    with a visual or conceptual request.

    Examples:
    - photos of Nisha at the beach
    - outdoor photos from 2022
    - pictures of cars taken in Mumbai
    """
    if semantic_query is not None:
        if not isinstance(semantic_query, str):
            return _error_response(
                "semantic_query must be a string or None."
            )

        semantic_query = semantic_query.strip()

        if not semantic_query:
            semantic_query = None

    if not isinstance(n_results, int):
        return _error_response(
            "n_results must be an integer."
        )

    if n_results < 1:
        return _error_response(
            "n_results must be at least 1."
        )

    if n_results > 100:
        return _error_response(
            "n_results cannot exceed 100."
        )

    try:
        results = _search_service.hybrid_search(
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

        return _serialize_results(results)

    except Exception as exc:
        return _error_response(
            f"Hybrid photo search failed: {exc}"
        )


# ============================================================
# LANGCHAIN TOOLS
# ============================================================

structured_photo_search = StructuredTool.from_function(
    func=structured_photo_search_tool,
    name="structured_photo_search",
    description=(
        "Search the photo database using exact structured metadata. "
        "Use this when the user specifies person names, years, "
        "dates, locations, camera information, or filenames. "
        "Do not use it for visual concepts that are not metadata."
    ),
)


semantic_photo_search = StructuredTool.from_function(
    func=semantic_photo_search_tool,
    name="semantic_photo_search",
    description=(
        "Search photos using natural-language visual similarity. "
        "Use this for visual or conceptual requests such as "
        "beaches, sunsets, food, vehicles, buildings, outdoor "
        "scenes, animals, celebrations, or similar concepts. "
        "Do not use this when exact metadata filtering is sufficient."
    ),
)


hybrid_photo_search = StructuredTool.from_function(
    func=hybrid_photo_search_tool,
    name="hybrid_photo_search",
    description=(
        "Search photos using both exact metadata filters and "
        "semantic visual similarity. Use this when a request "
        "combines metadata constraints with a visual concept, "
        "such as 'Nisha at the beach' or 'outdoor photos from 2022'."
    ),
)


PHOTO_SEARCH_TOOLS = [
    structured_photo_search,
    semantic_photo_search,
    hybrid_photo_search,
]
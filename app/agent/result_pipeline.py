from agent.result_extractor import (
    extract_raw_photo_results,
)
from agent.result_normalizer import (
    normalize_photo_results,
)


def extract_photo_results(response_messages):
    """
    Convert LangChain agent response messages into
    canonical PhotoAgent photo result dictionaries.
    """

    raw_results = extract_raw_photo_results(
        response_messages
    )

    return normalize_photo_results(
        raw_results
    )
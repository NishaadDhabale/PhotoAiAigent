import ast
import json


def _parse_content(content):
    """Parse a content payload into Python data."""

    if isinstance(content, (dict, list)):
        return content

    if not isinstance(content, str):
        return None

    text = content.strip()

    if not text:
        return None

    # JSON
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Python-style dict/list
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return None


def _extract_results_from_parsed(parsed):
    """Extract a results list from already-parsed content."""

    if isinstance(parsed, dict):
        results = parsed.get("results")

        if isinstance(results, list):
            return results

    elif isinstance(parsed, list):
        # A list may itself contain photo dictionaries.
        if all(isinstance(item, dict) for item in parsed):
            return parsed

    return []


def extract_raw_photo_results(response_messages):
    """
    Extract photo results from Agent/LangChain messages.

    Supports:
    1. ToolMessage JSON:
       {"count": 2, "results": [...]}

    2. Dictionary content

    3. JSON/Python-string content

    4. Gemini/LangChain content blocks:
       [{"type": "text", "text": "...JSON..."}]

    5. Direct list of photo dictionaries
    """

    extracted = []

    for message in response_messages:
        content = getattr(message, "content", None)

        # ---------------------------------------------------------
        # 1. Direct content
        # ---------------------------------------------------------
        parsed = _parse_content(content)

        results = _extract_results_from_parsed(parsed)

        if results:
            extracted.extend(results)

        # ---------------------------------------------------------
        # 2. Gemini/LangChain content blocks
        # ---------------------------------------------------------
        if isinstance(content, list):

            for block in content:

                if isinstance(block, dict):

                    # A block itself may contain a results payload.
                    block_results = _extract_results_from_parsed(block)

                    if block_results:
                        extracted.extend(block_results)
                        continue

                    # Or the useful JSON may be inside block["text"].
                    text = block.get("text")

                    if text:
                        parsed_text = _parse_content(text)
                        text_results = _extract_results_from_parsed(
                            parsed_text
                        )

                        if text_results:
                            extracted.extend(text_results)

    return extracted
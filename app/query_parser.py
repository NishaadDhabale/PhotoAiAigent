import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedQuery:
    """
    Interpreted user search query.

    Structured fields are used by SQLite.
    Remaining text is used for semantic search.
    """

    original: str
    semantic_query: Optional[str] = None
    person: Optional[str] = None
    year: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    camera: Optional[str] = None
    filename: Optional[str] = None

    @property
    def has_structured_filters(self) -> bool:
        return any(
            value is not None
            for value in (
                self.person,
                self.year,
                self.start_date,
                self.end_date,
                self.location,
                self.camera,
                self.filename,
            )
        )

    @property
    def has_semantic_query(self) -> bool:
        return bool(self.semantic_query)


# Words which commonly surround a structured search value.
_PREFIX_WORDS = {
    "photo",
    "photos",
    "picture",
    "pictures",
    "image",
    "images",
    "of",
    "from",
    "in",
    "taken",
    "takenon",
    "taken",
    "showing",
    "with",
    "by",
    "me",
    "the",
    "for",
    "my",
}


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _remove_phrases(text: str, phrases: list[str]) -> str:
    for phrase in phrases:
        text = re.sub(
            rf"\b{re.escape(phrase)}\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )

    return _clean_text(text)


def _extract_year(text: str) -> tuple[Optional[int], str]:
    """
    Extract a four-digit year in a reasonable photo range.

    We deliberately do not treat arbitrary four-digit numbers as years.
    """
    match = re.search(r"\b(19\d{2}|20\d{2})\b", text)

    if not match:
        return None, text

    year = int(match.group(1))

    # Remove only the matched year.
    remaining = (
        text[: match.start()] +
        " " +
        text[match.end():]
    )

    return year, _clean_text(remaining)


def _extract_person(text: str) -> tuple[Optional[str], str]:
    """
    Extract a known person name from the local people table.

    This intentionally queries the database rather than guessing names
    from arbitrary words.
    """
    try:
        from database import get_connection

        conn = get_connection()

        try:
            rows = conn.execute(
                """
                SELECT name
                FROM people
                WHERE name IS NOT NULL
                  AND TRIM(name) != ''
                ORDER BY LENGTH(name) DESC
                """
            ).fetchall()
        finally:
            conn.close()

    except Exception:
        return None, text

    for row in rows:
        name = row[0]

        if re.search(
            rf"\b{re.escape(name)}\b",
            text,
            flags=re.IGNORECASE,
        ):
            remaining = re.sub(
                rf"\b{re.escape(name)}\b",
                " ",
                text,
                flags=re.IGNORECASE,
            )

            return name, _clean_text(remaining)

    return None, text


def _extract_camera(text: str) -> tuple[Optional[str], str]:
    """
    Extract a camera value only when the query explicitly indicates
    that the user is searching by camera.
    """
    patterns = [
        r"\bcamera\s*[:=]?\s+(.+?)(?=\s+(?:from|in|of|for|with)\b|$)",
        r"\btaken\s+with\s+(.+?)(?=\s+(?:from|in|of|for)\b|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            camera = _clean_text(match.group(1))

            if camera:
                remaining = text[:match.start()] + " " + text[match.end():]
                return camera, _clean_text(remaining)

    return None, text


def _extract_filename(text: str) -> tuple[Optional[str], str]:
    """
    Extract explicit filename searches.

    Examples:
        filename IMG_20220124_213235.jpg
        file IMG_20220124_213235.jpg
    """
    pattern = r"\b(?:filename|file)\s*[:=]?\s*([^\s]+)"

    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None, text

    filename = match.group(1)

    remaining = text[:match.start()] + " " + text[match.end():]

    return filename, _clean_text(remaining)


def _cleanup_semantic_text(text: str) -> Optional[str]:
    """
    Remove search boilerplate while preserving actual semantic intent.
    """
    text = _clean_text(text)

    text = _remove_phrases(
    text,
    [
        "show me",
        "find me",
        "find",
        "search for",
        "search",
        "photos",
        "photo",
        "pictures",
        "picture",
        "images",
        "image",
        "please",
        "my",
    ],
)
    text = re.sub(
        r"\b(?:taken|captured)\s+(?:in|on)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = _clean_text(text)

    if not text:
        return None

    return text


def parse_query(query: Optional[str]) -> ParsedQuery:
    """
    Convert a natural-language search into structured filters
    plus an optional semantic query.

    Examples:

        Nisha
            -> person=Nisha

        photos from 2022
            -> year=2022

        Nisha 2022
            -> person=Nisha, year=2022

        Nisha at the beach
            -> person=Nisha, semantic_query="at the beach"

        photos at the beach
            -> semantic_query="at the beach"
    """
    original = _clean_text(query or "")

    if not original:
        return ParsedQuery(original="")

    working = original

    year, working = _extract_year(working)

    # When a year was extracted, remove the natural-language
    # connector that introduced the year.
    #
    # Examples:
    #   "photos from 2022" -> "photos"
    #   "photos in 2022"   -> "photos"
    #   "Nisha from 2022"  -> "Nisha"
    #
    # These words are meaningful in genuine semantic queries
    # such as "a photo from the beach", so only remove them
    # when a year was actually detected.
    if year is not None:
        working = re.sub(
            r"\b(?:from|in|on)\b",
            " ",
            working,
            flags=re.IGNORECASE,
        )
        working = _clean_text(working)

    person, working = _extract_person(working)

    camera, working = _extract_camera(working)

    filename, working = _extract_filename(working)

    semantic_query = _cleanup_semantic_text(working)

    return ParsedQuery(
        original=original,
        semantic_query=semantic_query,
        person=person,
        year=year,
        camera=camera,
        filename=filename,
    )
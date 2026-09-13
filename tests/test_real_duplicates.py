from app.database import get_all_photos
from app.duplicate_detector import (
    find_exact_duplicates,
    find_near_duplicates,
    DEFAULT_SIMILARITY_THRESHOLD,
)


def main():
    photos = get_all_photos()

    print(f"Photos in database: {len(photos)}")
    print()

    # --------------------------------------------------
    # Exact duplicates
    # --------------------------------------------------

    print("Checking exact duplicates...")

    exact_groups = find_exact_duplicates(photos)

    print(
        f"Exact duplicate groups: "
        f"{len(exact_groups)}"
    )

    for index, group in enumerate(
        exact_groups,
        start=1,
    ):
        print()
        print(f"Exact group {index}:")

        for photo in group:
            print(
                f"  [{photo['id']}] "
                f"{photo['filename']}"
            )

    print()

    # --------------------------------------------------
    # Near duplicates
    # --------------------------------------------------

    print(
        "Checking near duplicates "
        f"(threshold={DEFAULT_SIMILARITY_THRESHOLD})..."
    )

    matches = find_near_duplicates(
        photos,
        threshold=DEFAULT_SIMILARITY_THRESHOLD,
    )

    print(
        f"Near-duplicate pairs: "
        f"{len(matches)}"
    )

    for index, match in enumerate(
        matches,
        start=1,
    ):
        first = match["photo_a"]
        second = match["photo_b"]
        similarity = match["similarity"]

        print()
        print(f"Match {index}:")
        print(
            f"  [{first['id']}] "
            f"{first['filename']}"
        )
        print(
            f"  [{second['id']}] "
            f"{second['filename']}"
        )
        print(
            f"  similarity: "
            f"{similarity:.4f}"
        )

    print()
    print("DUPLICATE SCAN COMPLETE")
    print("No files were modified.")


if __name__ == "__main__":
    main()
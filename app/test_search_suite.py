from search import search_photos


def check(label, photos, expected_count):
    print(
        f"{label}: "
        f"{len(photos)} results"
    )

    assert len(photos) == expected_count


def main():

    # ---------------------------------
    # 1. Person
    # ---------------------------------

    photos = search_photos(
        person="Nisha"
    )

    check(
        "Person search",
        photos,
        5,
    )


    # ---------------------------------
    # 2. Person + year
    # ---------------------------------

    photos = search_photos(
        person="Nisha",
        year=2022,
    )

    check(
        "Person + year",
        photos,
        2,
    )


    # ---------------------------------
    # 3. Person + date range
    # ---------------------------------

    photos = search_photos(
        person="Nisha",
        start_date="2022:01:01 00:00:00",
        end_date="2022:03:31 23:59:59",
    )

    check(
        "Person + date range",
        photos,
        2,
    )


    # ---------------------------------
    # 4. Filename
    # ---------------------------------

    photos = search_photos(
        filename="IMG_2022"
    )

    check(
      "Filename search",
      photos,
      6,
    )


    # ---------------------------------
    # 5. Year alone
    # ---------------------------------

    photos = search_photos(
        year=2022
    )

    check(
        "Year search",
        photos,
        6,
    )


    # ---------------------------------
    # 6. Empty search
    # ---------------------------------

    photos = search_photos()

    check(
        "Empty search",
        photos,
        27,
    )


    # ---------------------------------
    # 7. Impossible search
    # ---------------------------------

    photos = search_photos(
        person="PersonThatDoesNotExist"
    )

    check(
        "Unknown person",
        photos,
        0,
    )


    print()
    print("All search tests passed.")


if __name__ == "__main__":
    main()
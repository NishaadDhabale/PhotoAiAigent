from people import find_photos_by_person_and_date_range


def main():
    photos = find_photos_by_person_and_date_range(
        "Nisha",
        "2022:01:01 00:00:00",
        "2022:03:31 23:59:59",
    )

    print(
        f"Found {len(photos)} photos "
        f"of Nisha in the date range"
    )

    for photo in photos:
        print(
            f"{photo['photo_id']}: "
            f"{photo['filename']}"
        )


if __name__ == "__main__":
    main()
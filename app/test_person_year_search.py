from people import find_photos_by_person_and_year


def main():
    photos = find_photos_by_person_and_year(
        "Nisha",
        2022,
    )

    print(
        f"Found {len(photos)} photos of Nisha in 2022"
    )

    for photo in photos:
        print(
            f"{photo['photo_id']}: "
            f"{photo['filename']}"
        )


if __name__ == "__main__":
    main()
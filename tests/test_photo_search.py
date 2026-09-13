from app.people import find_photos_by_person


def main():
    photos = find_photos_by_person("Nisha")

    print(
        f"Found {len(photos)} photos"
    )

    for photo in photos:
        print(
            f"{photo['photo_id']}: "
            f"{photo['filename']}"
        )


if __name__ == "__main__":
    main()
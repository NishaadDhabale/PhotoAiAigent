from app.search import search_photos


def main():
    photos = search_photos(
        person="Nisha",
    )

    print(
        f"Found {len(photos)} photos"
    )

    for photo in photos:
        print(
            f"{photo['photo_id']}: "
            f"{photo['filename']} | "
            f"{photo['date_taken']}"
        )


if __name__ == "__main__":
    main()
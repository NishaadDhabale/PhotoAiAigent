from app.search import search_photos


def main():
    photos = search_photos(
        person="Nisha",
        start_date="2022:01:01 00:00:00",
        end_date="2022:12:31 23:59:59",
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
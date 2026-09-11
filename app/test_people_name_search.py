from database import get_photos_by_person_name


def main():
    photos = get_photos_by_person_name("Nisha")

    print(f"Photos containing Nisha: {len(photos)}")

    print()

    for photo_id, filename, path in photos:
        print(f"{photo_id}: {filename}")


if __name__ == "__main__":
    main()
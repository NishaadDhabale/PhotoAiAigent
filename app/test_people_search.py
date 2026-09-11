from database import get_photos_by_person_group


def main():
    group_id = 1

    photos = get_photos_by_person_group(group_id)

    print(
        f"Photos containing person group {group_id}: "
        f"{len(photos)}"
    )

    print()

    for photo_id, filename, path in photos:
        print(
            f"{photo_id}: {filename}"
        )


if __name__ == "__main__":
    main()
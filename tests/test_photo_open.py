from app.database import get_all_photos
from app.photo_access import open_photo
from app.photo_results import photos_from_dicts


def main():
    print("=" * 60)
    print("PhotoAgent Local Photo Viewer Test")
    print("=" * 60)

    rows = get_all_photos()
    photos = photos_from_dicts(rows)

    print(f"\nFound {len(photos)} photos.\n")

    for index, photo in enumerate(photos, start=1):
        print(f"[{index}] {photo.filename}")

    print()
    print("Type a number to open a photo.")
    print("Type 'exit' to quit.")

    while True:
        choice = input("\nOpen > ").strip()

        if choice.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        try:
            number = int(choice)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if number < 1 or number > len(photos):
            print(
                f"Invalid number. Choose between 1 and {len(photos)}."
            )
            continue

        photo = photos[number - 1]

        print(f"Opening: {photo.filename}")
        print(f"Path: {photo.path}")

        try:
            open_photo(photo)
            print("Photo opened successfully.")

        except Exception as exc:
            print(f"Failed to open photo: {exc}")


if __name__ == "__main__":
    main()
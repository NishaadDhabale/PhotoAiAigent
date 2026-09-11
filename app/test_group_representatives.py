from database import get_unidentified_group_representatives


def main():
    groups = get_unidentified_group_representatives()

    print(
        f"Unidentified group representatives: "
        f"{len(groups)}"
    )

    print()

    for row in groups:
        (
            group_id,
            face_id,
            photo_id,
            filename,
            path,
            face_index,
            confidence,
        ) = row

        print(
            f"Group {group_id}: "
            f"{filename} | "
            f"face {face_index} | "
            f"confidence={confidence:.3f}"
        )


if __name__ == "__main__":
    main()
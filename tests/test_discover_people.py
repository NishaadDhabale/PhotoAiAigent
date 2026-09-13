from app.database import discover_people


def main():
    result = discover_people()

    print(
        f"Known people: "
        f"{len(result['known_people'])}"
    )

    print(
        f"Unidentified groups: "
        f"{len(result['unidentified_groups'])}"
    )

    print()

    for person_id, name, group_id in result["known_people"]:
        print(
            f"Known: {name} "
            f"(person_id={person_id}, group={group_id})"
        )

    print()

    for row in result["unidentified_groups"]:
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
            f"Unknown group {group_id}: "
            f"{filename}, "
            f"face={face_index}, "
            f"confidence={confidence:.3f}"
        )


if __name__ == "__main__":
    main()
from database import get_people


def main():
    people = get_people()

    print(f"Known people: {len(people)}")

    for person_id, name, group_id in people:
        print(
            f"Person {person_id}: "
            f"{name} "
            f"(group {group_id})"
        )


if __name__ == "__main__":
    main()
from database import (
    delete_person,
    get_person_by_group,
)
from people import discover


def main():
    person = get_person_by_group(4)

    if person is None:
        print("No person found for group 4")
        return

    person_id = person[0]

    print(f"Deleting test person: {person}")

    deleted = delete_person(person_id)

    print(f"Rows deleted: {deleted}")

    result = discover()

    print()
    print(
        f"Known people: "
        f"{len(result['known_people'])}"
    )

    print(
        f"Unidentified groups: "
        f"{len(result['unidentified_groups'])}"
    )


if __name__ == "__main__":
    main()
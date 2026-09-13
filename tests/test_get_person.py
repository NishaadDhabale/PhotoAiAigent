from app.database import (
    get_person_by_group,
    update_person_name,
)


def main():
    person = get_person_by_group(1)

    if person is None:
        print("Person not found")
        return

    person_id = person[0]

    updated = update_person_name(
        person_id,
        "Nisha",
    )

    print(f"Rows updated: {updated}")

    person = get_person_by_group(1)

    print(f"Person for group 1: {person}")


if __name__ == "__main__":
    main()
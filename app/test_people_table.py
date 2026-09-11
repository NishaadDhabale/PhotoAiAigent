import sqlite3

from database import DATABASE_PATH, create_person


def main():
    person_id = create_person(1)

    print(f"Created person: {person_id}")

    connection = sqlite3.connect(DATABASE_PATH)

    row = connection.execute(
        """
        SELECT id, name, person_group_id
        FROM people
        WHERE id = ?
        """,
        (person_id,),
    ).fetchone()

    connection.close()

    print(f"Database record: {row}")


if __name__ == "__main__":
    main()
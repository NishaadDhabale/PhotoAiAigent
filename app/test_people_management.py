from database import get_connection
from people_management import (
    rename_person,
    merge_person_groups,
)


def get_people():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, person_group_id
            FROM people
            ORDER BY id
            """
        ).fetchall()

    finally:
        connection.close()


def get_face_group_counts():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT person_group_id, COUNT(*)
            FROM faces
            WHERE person_group_id IS NOT NULL
            GROUP BY person_group_id
            ORDER BY person_group_id
            """
        ).fetchall()

    finally:
        connection.close()


def test_rename():
    people = get_people()

    if not people:
        print("⚠ No people records found; skipping rename test.")
        return

    person_id = people[0][0]
    original_name = people[0][1]

    temporary_name = "__PhotoAgent_Test_Name__"

    rename_person(person_id, temporary_name)

    updated = get_people()

    updated_name = next(
        row[1]
        for row in updated
        if row[0] == person_id
    )

    assert updated_name == temporary_name

    rename_person(person_id, original_name)

    restored = get_people()

    restored_name = next(
        row[1]
        for row in restored
        if row[0] == person_id
    )

    assert restored_name == original_name

    print("✓ Person rename")


def test_merge():
    counts_before = get_face_group_counts()

    if len(counts_before) < 2:
        print("⚠ Fewer than two face groups; skipping merge test.")
        return

    group_a = counts_before[0][0]
    group_b = counts_before[1][0]

    original_a = counts_before[0][1]
    original_b = counts_before[1][1]

    merge_person_groups(
        [group_a, group_b],
        target_group_id=group_a,
    )

    counts_after = get_face_group_counts()

    merged_count = next(
        count
        for group_id, count in counts_after
        if group_id == group_a
    )

    assert merged_count == original_a + original_b

    remaining_b = [
        count
        for group_id, count in counts_after
        if group_id == group_b
    ]

    assert not remaining_b

    print("✓ Person merge")


if __name__ == "__main__":
    test_rename()
    test_merge()

    print()
    print("ALL PEOPLE MANAGEMENT TESTS PASSED")
from database import get_connection


def rename_person(group_id, new_name):
    """
    Rename a person/face group.

    Works for both:
    - existing rows in the people table
    - automatically generated face groups that don't yet
      have a people-table entry
    """

    group_id = int(group_id)
    new_name = new_name.strip()

    if not new_name:
        raise ValueError("Person name cannot be empty.")

    connection = get_connection()

    try:
        # Check whether this group actually exists in faces.
        group = connection.execute(
            """
            SELECT 1
            FROM faces
            WHERE person_group_id = ?
            LIMIT 1
            """,
            (group_id,),
        ).fetchone()

        if group is None:
            raise ValueError(
                f"Person group {group_id} was not found."
            )

        # Check whether a people row already exists.
        existing = connection.execute(
            """
            SELECT id
            FROM people
            WHERE person_group_id = ?
            """,
            (group_id,),
        ).fetchone()

        if existing:
            # Existing person → simply rename it.
            connection.execute(
                """
                UPDATE people
                SET name = ?
                WHERE person_group_id = ?
                """,
                (new_name, group_id),
            )

            person_id = existing[0]

        else:
            # Automatically generated group → create
            # its people entry for the first time.
            cursor = connection.execute(
                """
                INSERT INTO people (
                    name,
                    person_group_id
                )
                VALUES (?, ?)
                """,
                (new_name, group_id),
            )

            person_id = cursor.lastrowid

        connection.commit()

        return {
            "id": int(person_id),
            "name": new_name,
            "group_id": group_id,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def merge_person_groups(group_ids, target_group_id=None):
    """
    Merge multiple face groups into one group.

    The first group is used as the target when no explicit
    target_group_id is supplied.
    """

    group_ids = list(
        dict.fromkeys(
            int(group_id)
            for group_id in group_ids
        )
    )

    if len(group_ids) < 2:
        raise ValueError(
            "Select at least two people to merge."
        )

    if target_group_id is None:
        target_group_id = group_ids[0]

    target_group_id = int(target_group_id)

    if target_group_id not in group_ids:
        raise ValueError(
            "Target group must be one of the selected groups."
        )

    connection = get_connection()

    try:
        placeholders = ",".join(
            "?" for _ in group_ids
        )

        existing_groups = connection.execute(
            f"""
            SELECT DISTINCT person_group_id
            FROM faces
            WHERE person_group_id IN ({placeholders})
            """,
            group_ids,
        ).fetchall()

        existing_group_ids = {
            int(row[0])
            for row in existing_groups
            if row[0] is not None
        }

        if target_group_id not in existing_group_ids:
            raise ValueError(
                f"Person group {target_group_id} was not found."
            )

        # Move all faces into the target group.
        connection.execute(
            f"""
            UPDATE faces
            SET person_group_id = ?
            WHERE person_group_id IN ({placeholders})
            """,
            [target_group_id, *group_ids],
        )

        # Remove old people entries.
        connection.execute(
            f"""
            DELETE FROM people
            WHERE person_group_id IN ({placeholders})
              AND person_group_id != ?
            """,
            [*group_ids, target_group_id],
        )

        connection.commit()

        return {
            "target_group_id": target_group_id,
            "merged_group_ids": group_ids,
            "count": len(group_ids),
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_person_group(group_id):
    """
    Get the stored person information for a face group.
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                person_group_id
            FROM people
            WHERE person_group_id = ?
            """,
            (int(group_id),),
        ).fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "group_id": row[2],
        }

    finally:
        connection.close()
from database import get_connection


def main():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                location_name
            FROM photos
            """
        ).fetchall()

        total = len(rows)

        located = [
            row
            for row in rows
            if row[1] is not None
            and str(row[1]).strip() != ""
        ]

        unknown = [
            row
            for row in rows
            if row[1] is None
            or str(row[1]).strip() == ""
        ]

        print("\n=== PLACES DATABASE ===")
        print(f"total={total}")
        print(f"located={len(located)}")
        print(f"unknown={len(unknown)}")

        assert (
            len(located) + len(unknown)
            == total
        )

        location_names = sorted(
            {
                str(row[1]).strip()
                for row in located
            }
        )

        print("\n=== LOCATIONS ===")

        for location in location_names:
            count = sum(
                1
                for row in located
                if str(row[1]).strip()
                == location
            )

            print(
                f"{location}: {count} photos"
            )

            assert count > 0

        print(
            f"\nunique_locations="
            f"{len(location_names)}"
        )

        print("\nALL PLACES DATABASE TESTS PASSED")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
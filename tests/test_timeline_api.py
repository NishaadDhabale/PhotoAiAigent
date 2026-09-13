from app.database import get_connection


MONTH_NAMES = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def main():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT id, filename, date_taken
            FROM photos
            ORDER BY
                CASE
                    WHEN date_taken IS NULL THEN 1
                    ELSE 0
                END,
                date_taken DESC,
                id DESC
            """
        ).fetchall()

        total = len(rows)

        dated = [
            row for row in rows
            if row[2]
        ]

        undated = [
            row for row in rows
            if not row[2]
        ]

        print("\n=== TIMELINE DATABASE ===")
        print(f"total={total}")
        print(f"dated={len(dated)}")
        print(f"undated={len(undated)}")

        # Basic dataset checks
        assert total == 27
        assert len(dated) == 11
        assert len(undated) == 16

        assert (
            len(dated) + len(undated)
            == total
        )

        # Group dated photos
        grouped = {}

        for row in dated:
            date_string = row[2]

            year = int(date_string[:4])
            month = int(date_string[5:7])

            assert 1 <= month <= 12

            grouped.setdefault(
                year,
                {}
            ).setdefault(
                month,
                []
            ).append(row)

        print("\n=== YEARS ===")

        years = sorted(
            grouped.keys(),
            reverse=True,
        )

        for year in years:
            year_count = sum(
                len(photos)
                for photos in grouped[year].values()
            )

            print(
                f"{year}: {year_count} photos"
            )

            previous_month = None

            for month in sorted(
                grouped[year].keys(),
                reverse=True,
            ):
                photos = grouped[year][month]

                print(
                    f"  {MONTH_NAMES[month]}: "
                    f"{len(photos)} photos"
                )

                # Months must be descending
                if previous_month is not None:
                    assert month < previous_month

                previous_month = month

        # Current dataset's dated years
        assert years == [
            2023,
            2022,
            2019,
        ]

        # Years must be descending
        assert years == sorted(
            years,
            reverse=True,
        )

        # Verify every dated photo has
        # a valid YYYY:MM structure.
        for row in dated:
            date_string = row[2]

            assert len(date_string) >= 7
            assert date_string[4] == ":"
            assert date_string[7] == " "

            month = int(
                date_string[5:7]
            )

            assert 1 <= month <= 12

        print("\nALL TIMELINE DATABASE TESTS PASSED")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
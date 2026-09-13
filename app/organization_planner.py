from pathlib import Path

from database import get_all_photos


def plan_by_year():
    """
    Create a read-only organization plan based on photo year.

    No files or directories are created, moved, renamed, or deleted.
    """

    photos = get_all_photos()
    plan = []

    for photo in photos:
        source = Path(photo["path"])

        date_taken = photo.get("date_taken")

        if date_taken:
            year = str(date_taken)[:4]

            if not year.isdigit():
                year = "Undated"
        else:
            year = "Undated"

        # If the photo is already inside the correct year folder,
        # its destination is its current location.
        if source.parent.name == year:
            destination = source
        else:
            destination = source.parent / year / source.name

        # Determine safety status.
        if not source.exists():
            status = "MISSING_SOURCE"

        elif destination == source:
            status = "ALREADY_ORGANIZED"

        elif destination.exists():
            status = "CONFLICT"

        else:
            status = "SAFE"

        plan.append({
            "photo_id": photo["id"],
            "filename": photo["filename"],
            "source": str(source),
            "destination": str(destination),
            "year": year,
            "status": status,
        })

    return plan


def print_plan(plan):
    """Display an organization plan without modifying files."""

    print("\n" + "=" * 60)
    print("PHOTO ORGANIZATION PREVIEW")
    print("=" * 60)

    if not plan:
        print("No photos found.")
        return

    grouped = {}

    for item in plan:
        grouped.setdefault(item["year"], []).append(item)

    for year in sorted(grouped):
        print(f"\n{year}/")

        for item in grouped[year]:
            print(
                f"  [{item['status']}] "
                f"{item['filename']}"
            )

    safe = sum(
        item["status"] == "SAFE"
        for item in plan
    )

    conflicts = sum(
        item["status"] == "CONFLICT"
        for item in plan
    )

    organized = sum(
        item["status"] == "ALREADY_ORGANIZED"
        for item in plan
    )

    missing = sum(
        item["status"] == "MISSING_SOURCE"
        for item in plan
    )

    print("\n" + "-" * 60)
    print(f"Photos:            {len(plan)}")
    print(f"Safe to move:      {safe}")
    print(f"Conflicts:         {conflicts}")
    print(f"Already organized: {organized}")
    print(f"Missing source:    {missing}")
    print("-" * 60)
    print("NO FILES WERE MODIFIED.")
    print("=" * 60)


if __name__ == "__main__":
    plan = plan_by_year()
    print_plan(plan)
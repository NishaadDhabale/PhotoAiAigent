from database import (
    create_person,
    discover_people,
    get_person,
    get_person_by_group,
    get_photos_by_person_name,
    get_photos_by_person_name_and_date_range,
    person_group_exists,
    update_person_name,
)


def identify_group(person_group_id, name):
    if not person_group_exists(person_group_id):
        raise ValueError(
            f"Person group {person_group_id} does not exist"
        )

    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "Person name cannot be empty"
        )

    name = name.strip()

    existing_person = get_person_by_group(person_group_id)

    if existing_person:
        person_id = existing_person[0]

        update_person_name(
            person_id,
            name,
        )

        return person_id

    return create_person(
        person_group_id,
        name,
    )


def search_person(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "Person name cannot be empty"
        )

    return get_photos_by_person_name(
        name.strip()
    )


def get_person_details(person_id):
    return get_person(person_id)


def discover():
    return discover_people()

def find_photos_by_person(name):
    photos = search_person(name)

    return [
        {
            "photo_id": photo_id,
            "filename": filename,
            "path": path,
        }
        for photo_id, filename, path in photos
    ]



def find_photos_by_person_and_year(name, year):
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "Person name cannot be empty"
        )

    return [
        {
            "photo_id": photo_id,
            "filename": filename,
            "path": path,
        }
        for photo_id, filename, path
        in get_photos_by_person_name_and_year(
            name.strip(),
            year,
        )
    ]


def find_photos_by_person_and_date_range(
    name,
    start_date,
    end_date,
):
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "Person name cannot be empty"
        )

    if start_date > end_date:
        raise ValueError(
            "Start date cannot be after end date"
        )

    photos = get_photos_by_person_name_and_date_range(
        name.strip(),
        start_date,
        end_date,
    )

    return [
        {
            "photo_id": photo_id,
            "filename": filename,
            "path": path,
        }
        for photo_id, filename, path in photos
    ]
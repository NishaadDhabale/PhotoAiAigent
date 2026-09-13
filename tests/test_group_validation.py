from app.people import identify_group


def main():
    person_id = identify_group(
        1,
        "Nisha",
    )

    print(
        f"Valid group accepted: "
        f"person_id={person_id}"
    )

    try:
        identify_group(
            999,
            "Invalid Person",
        )
    except ValueError as error:
        print(
            f"Invalid group rejected: "
            f"{error}"
        )


if __name__ == "__main__":
    main()
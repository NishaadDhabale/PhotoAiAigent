from people import identify_group


def main():
    person_id = identify_group(
        1,
        "  Nisha  ",
    )

    print(
        f"Name normalized successfully: "
        f"person_id={person_id}"
    )

    for invalid_name in ["", "   "]:
        try:
            identify_group(
                1,
                invalid_name,
            )
        except ValueError as error:
            print(
                f"Invalid name rejected: "
                f"{error}"
            )


if __name__ == "__main__":
    main()
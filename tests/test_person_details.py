from app.people import get_person_details


def main():
    person = get_person_details(1)

    print(f"Person: {person}")


if __name__ == "__main__":
    main()
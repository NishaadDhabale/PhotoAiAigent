from agent.result_manager import PhotoResultManager
from photo_result import PhotoResult


def make_photo(photo_id, filename):
    return PhotoResult(
        id=photo_id,
        filename=filename,
        path=f"D:/Photos/{filename}",
    )


def test_empty_manager():
    print("Test 1: Empty manager")

    manager = PhotoResultManager()

    assert len(manager) == 0
    assert manager.get_results() == []

    print("Empty manager: OK")


def test_set_results():
    print("\nTest 2: Set results")

    manager = PhotoResultManager()

    photos = [
        make_photo(1, "photo1.jpg"),
        make_photo(2, "photo2.jpg"),
        make_photo(3, "photo3.jpg"),
    ]

    manager.set_results(photos)

    assert len(manager) == 3
    assert manager.get_results() == photos

    print("Set results: OK")


def test_get_by_number():
    print("\nTest 3: Get photo by display number")

    manager = PhotoResultManager()

    photos = [
        make_photo(10, "first.jpg"),
        make_photo(20, "second.jpg"),
        make_photo(30, "third.jpg"),
    ]

    manager.set_results(photos)

    first = manager.get(1)
    second = manager.get(2)
    third = manager.get(3)

    assert first.id == 10
    assert second.id == 20
    assert third.id == 30

    print("Number lookup: OK")


def test_invalid_number():
    print("\nTest 4: Invalid photo numbers")

    manager = PhotoResultManager()

    manager.set_results(
        [
            make_photo(1, "photo1.jpg"),
            make_photo(2, "photo2.jpg"),
        ]
    )

    try:
        manager.get(0)
        assert False, "Expected IndexError"

    except IndexError:
        pass

    try:
        manager.get(3)
        assert False, "Expected IndexError"

    except IndexError:
        pass

    print("Invalid number handling: OK")


def test_clear():
    print("\nTest 5: Clear results")

    manager = PhotoResultManager()

    manager.set_results(
        [
            make_photo(1, "photo1.jpg"),
        ]
    )

    assert len(manager) == 1

    manager.clear()

    assert len(manager) == 0
    assert manager.get_results() == []

    print("Clear results: OK")


def test_copy_safety():
    print("\nTest 6: Result list isolation")

    manager = PhotoResultManager()

    photos = [
        make_photo(1, "photo1.jpg"),
    ]

    manager.set_results(photos)

    returned = manager.get_results()

    returned.clear()

    assert len(manager) == 1

    print("Result list isolation: OK")


def main():
    print("=" * 60)
    print("PhotoAgent Result Manager Test")
    print("=" * 60)

    test_empty_manager()
    test_set_results()
    test_get_by_number()
    test_invalid_number()
    test_clear()
    test_copy_safety()

    print("\n" + "=" * 60)
    print("ALL RESULT MANAGER TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
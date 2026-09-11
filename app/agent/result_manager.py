from photo_result import PhotoResult


class PhotoResultManager:
    """
    Maintains the photo results from the most recent search.
    """

    def __init__(self):
        self._results = []

    def set_results(self, results):
        """
        Replace the current results.
        """

        self._results = list(results)

    def clear(self):
        """
        Clear the current results.
        """

        self._results = []

    def get_results(self):
        """
        Return the current results.
        """

        return list(self._results)

    def get(self, number: int) -> PhotoResult:
        """
        Get a photo using a 1-based display number.
        """

        if not self._results:
            raise IndexError("No photo results available.")

        if number < 1 or number > len(self._results):
            raise IndexError(
                f"Photo number must be between 1 and "
                f"{len(self._results)}."
            )

        return self._results[number - 1]

    def __len__(self):
        return len(self._results)
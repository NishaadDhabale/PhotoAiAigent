from duplicate_detector import (
    DEFAULT_SIMILARITY_THRESHOLD,
    find_exact_duplicates,
    find_near_duplicates,
)
from database import get_all_photos


class DuplicateService:
    """
    Read-only service for detecting exact and near duplicates.
    """

    def __init__(
        self,
        threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        self.threshold = threshold

    def find_duplicates(self):
        photos = get_all_photos()

        exact_groups = find_exact_duplicates(
            photos
        )

        near_duplicates = find_near_duplicates(
            photos,
            threshold=self.threshold,
        )

        return {
            "total_photos": len(photos),
            "exact_groups": exact_groups,
            "near_duplicates": near_duplicates,
            "threshold": self.threshold,
        }
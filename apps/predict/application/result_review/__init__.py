"""Read-only Result Review application projection."""

from .clipboard import ResultReviewClipboardDocument
from .contracts import RESULT_REVIEW_COLUMNS, ResultReviewRow
from .projection import ResultReviewProjection

__all__ = [
    "RESULT_REVIEW_COLUMNS",
    "ResultReviewClipboardDocument",
    "ResultReviewProjection",
    "ResultReviewRow",
]

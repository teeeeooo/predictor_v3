"""Filesystem publication for Result Review CSV documents."""

from __future__ import annotations

from pathlib import Path

from apps.predict.application.result_review import ResultReviewClipboardDocument


def publish_result_review_csv(
    path: str | Path,
    document: ResultReviewClipboardDocument,
    *,
    encoding: str = "utf-8-sig",
) -> None:
    """Publish one already-shaped Result Review document without reinterpretation."""
    with Path(path).open("w", encoding=encoding, newline="") as handle:
        handle.write(document.to_csv())

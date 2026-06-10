"""Toolkit-neutral view models for calculator result summaries."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ResultSummary", "result_status"]


@dataclass(frozen=True)
class ResultSummary:
    """One user-facing metric summary card with already formatted values."""

    title: str
    fields: tuple[tuple[str, str], ...]
    status: str = "계산 완료"

    def as_text(self) -> str:
        """Return a compact clipboard-friendly rendering."""
        if not self.fields:
            return f"[{self.title}]\n{self.status}"
        headers = " | ".join(label for label, _value in self.fields)
        values = " | ".join(value for _label, value in self.fields)
        return f"[{self.title}]\n{headers}\n{values}\n{self.status}"


def result_status(title: str, status: str) -> ResultSummary:
    """Represent validation or calculation status without raw detail output."""
    return ResultSummary(title=title, fields=(), status=status)

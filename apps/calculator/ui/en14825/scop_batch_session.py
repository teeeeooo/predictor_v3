"""Profile-local state for dynamic EN14825 SCOP batch matrices."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec

__all__ = [
    "En14825ScopBatchActiveConditions",
    "En14825ScopBatchSessionState",
    "En14825ScopBatchSnapshot",
]


@dataclass(frozen=True)
class En14825ScopBatchActiveConditions:
    climate: str
    tbiv_temp_c: float
    tol_temp_c: float


@dataclass(frozen=True)
class En14825ScopBatchSnapshot:
    common_values: Mapping[str, str]
    active_conditions: En14825ScopBatchActiveConditions
    cases: tuple[Mapping[str, str], ...]


class En14825ScopBatchSessionState:
    """Preserve user inputs across profile-local matrix shape changes."""

    _POINT_KEYS = ("a", "b", "c", "d", "tol", "tbiv")
    _INPUT_KEYS = frozenset(
        {"p_design_h"}
        | {
            f"{point}_{measurement}"
            for point in _POINT_KEYS
            for measurement in ("capacity", "power")
        }
    )

    def __init__(
        self,
        active_conditions: En14825ScopBatchActiveConditions,
        cases: Sequence[Mapping[str, str]] = (),
    ) -> None:
        self.active_conditions = active_conditions
        self._case_store = [self._normalize_case(case) for case in cases] or [{}]

    @property
    def case_count(self) -> int:
        return len(self._case_store)

    def set_active_conditions(
        self,
        conditions: En14825ScopBatchActiveConditions,
    ) -> None:
        self.active_conditions = conditions

    def sync_visible_cases(
        self,
        cases: Sequence[Mapping[str, str]],
        visible_input_keys: Sequence[str],
    ) -> None:
        visible = self._INPUT_KEYS.intersection(visible_input_keys)
        target_count = max(1, len(cases))
        while len(self._case_store) < target_count:
            self._case_store.append({})
        del self._case_store[target_count:]
        for index, case in enumerate(cases):
            stored = self._case_store[index]
            for key in visible:
                stored[key] = str(case.get(key, ""))

    def visible_cases(self, spec: BatchMatrixSpec) -> tuple[dict[str, str], ...]:
        visible = set(spec.input_keys)
        return tuple(
            {key: value for key, value in case.items() if key in visible}
            for case in self._case_store
        )

    def add_case(self) -> None:
        self._case_store.append({})

    def remove_case(self) -> None:
        if len(self._case_store) > 1:
            self._case_store.pop()

    def snapshot(self, common_values: Mapping[str, str]) -> En14825ScopBatchSnapshot:
        return En14825ScopBatchSnapshot(
            common_values=MappingProxyType(dict(common_values)),
            active_conditions=self.active_conditions,
            cases=tuple(MappingProxyType(dict(case)) for case in self._case_store),
        )

    @classmethod
    def _normalize_case(cls, case: Mapping[str, str]) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in case.items()
            if key in cls._INPUT_KEYS
        }

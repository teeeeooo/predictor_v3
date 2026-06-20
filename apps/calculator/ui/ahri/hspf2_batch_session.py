"""Profile-local superset state for dynamic AHRI HSPF2 batch matrices."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from apps.calculator.ui.ahri.hspf2_batch import AhriHspf2BatchActiveOptions
from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec


@dataclass(frozen=True)
class AhriHspf2BatchSnapshot:
    common_values: Mapping[str, str]
    active_options: AhriHspf2BatchActiveOptions
    cases: tuple[Mapping[str, str], ...]


class AhriHspf2BatchSessionState:
    """Keep hidden optional inputs while projecting the active matrix."""

    _POINTS = ("H01", "H11", "H1N", "H2Int", "H32", "H42", "H12", "H22")
    _INPUT_KEYS = frozenset(
        {"a2_capacity", "a2_power"}
        | {
            f"{measurement}_{point}"
            for point in _POINTS
            for measurement in ("capacity", "power")
        }
    )

    def __init__(
        self,
        active_options: AhriHspf2BatchActiveOptions,
        cases: Sequence[Mapping[str, str]] = (),
    ) -> None:
        self.active_options = active_options
        self._case_store = [self._normalize(case) for case in cases] or [{}]

    @property
    def case_count(self) -> int:
        return len(self._case_store)

    def set_active_options(self, active: AhriHspf2BatchActiveOptions) -> None:
        self.active_options = active

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
            for key in visible:
                self._case_store[index][key] = str(case.get(key, ""))

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

    def snapshot(self, common: Mapping[str, str]) -> AhriHspf2BatchSnapshot:
        return AhriHspf2BatchSnapshot(
            MappingProxyType(dict(common)),
            self.active_options,
            tuple(MappingProxyType(dict(case)) for case in self._case_store),
        )

    @classmethod
    def _normalize(cls, case: Mapping[str, str]) -> dict[str, str]:
        return {key: str(value) for key, value in case.items() if key in cls._INPUT_KEYS}

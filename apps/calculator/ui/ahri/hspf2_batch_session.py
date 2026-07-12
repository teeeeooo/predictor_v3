"""Product-local superset state for dynamic AHRI HSPF2 batch matrices."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Sequence

from apps.calculator.ui.ahri.hspf2_batch import AhriHspf2BatchActiveOptions
from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec


@dataclass(frozen=True)
class AhriHspf2BatchSnapshot:
    common_values: Mapping[str, str]
    active_options: AhriHspf2BatchActiveOptions
    cases: tuple[Mapping[str, str], ...]
    product_cases: Mapping[str, tuple[Mapping[str, str], ...]] = field(default_factory=dict)


class AhriHspf2BatchSessionState:
    """Keep a separate hidden-input store for every product classification."""

    _POINTS = (
        "H01", "H11", "H1N", "H2Int", "H32", "H42", "H12", "H22",
        "H0Low", "H1Low", "H1Full", "H2Low", "H2Full", "H3Low", "H3Full",
        "H4Full", "H2Boost", "H3Boost", "H4Boost",
    )
    _INPUT_KEYS = frozenset(
        {"a2_capacity"}
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
        product_cases: Mapping[str, Sequence[Mapping[str, str]]] | None = None,
    ) -> None:
        self.active_options = active_options
        self._stores: dict[str, list[dict[str, str]]] = {
            product: [self._normalize(case) for case in saved] or [{}]
            for product, saved in (product_cases or {}).items()
        }
        product = active_options.product_classification
        if product not in self._stores:
            self._stores[product] = [self._normalize(case) for case in cases] or [{}]

    @property
    def _case_store(self) -> list[dict[str, str]]:
        return self._stores.setdefault(self.active_options.product_classification, [{}])

    @property
    def case_count(self) -> int:
        return len(self._case_store)

    def set_active_options(self, active: AhriHspf2BatchActiveOptions) -> None:
        self.active_options = active
        self._stores.setdefault(active.product_classification, [{}])

    def sync_visible_cases(
        self,
        cases: Sequence[Mapping[str, str]],
        visible_input_keys: Sequence[str],
    ) -> None:
        visible = self._INPUT_KEYS.intersection(visible_input_keys)
        target_count = max(1, len(cases))
        store = self._case_store
        while len(store) < target_count:
            store.append({})
        del store[target_count:]
        for index, case in enumerate(cases):
            for key in visible:
                store[index][key] = str(case.get(key, ""))

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
        product_cases = {
            product: tuple(MappingProxyType(dict(case)) for case in cases)
            for product, cases in self._stores.items()
        }
        return AhriHspf2BatchSnapshot(
            MappingProxyType(dict(common)),
            self.active_options,
            tuple(MappingProxyType(dict(case)) for case in self._case_store),
            MappingProxyType(product_cases),
        )

    @classmethod
    def _normalize(cls, case: Mapping[str, str]) -> dict[str, str]:
        return {key: str(value) for key, value in case.items() if key in cls._INPUT_KEYS}

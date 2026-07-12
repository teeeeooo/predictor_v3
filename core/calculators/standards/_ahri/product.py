"""AHRI product-path classification shared by stable facades and capability requests."""

from __future__ import annotations

VARIABLE_CAPACITY = "variable_capacity"
DUAL_STAGE = "dual_stage"
TRIPLE_CAPACITY_NORTHERN = "triple_capacity_northern"

_SEER2_PRODUCTS = frozenset({VARIABLE_CAPACITY, DUAL_STAGE})
_HSPF2_PRODUCTS = frozenset(
    {VARIABLE_CAPACITY, DUAL_STAGE, TRIPLE_CAPACITY_NORTHERN}
)


def normalize_product_classification(value: str | None, *, metric: str) -> str:
    """Return a validated semantic product classification for one AHRI metric."""
    product = VARIABLE_CAPACITY if value is None else str(value).strip().lower()
    aliases = {
        "variable": VARIABLE_CAPACITY,
        "variable capacity": VARIABLE_CAPACITY,
        "dual": DUAL_STAGE,
        "dual stage": DUAL_STAGE,
        "two_stage": DUAL_STAGE,
        "two-stage": DUAL_STAGE,
        "triple": TRIPLE_CAPACITY_NORTHERN,
        "triple stage northern": TRIPLE_CAPACITY_NORTHERN,
        "triple_stage_northern": TRIPLE_CAPACITY_NORTHERN,
    }
    product = aliases.get(product, product)
    metric_key = metric.strip().upper()
    supported = _SEER2_PRODUCTS if metric_key == "SEER2" else _HSPF2_PRODUCTS
    if metric_key not in {"SEER2", "HSPF2"}:
        raise ValueError(f"Unsupported AHRI metric: {metric!r}")
    if product not in supported:
        raise ValueError(
            f"Unsupported AHRI {metric_key} product classification: {product!r}; "
            f"supported={sorted(supported)}"
        )
    return product

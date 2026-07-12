"""Numeric primitives with identical semantics across extracted AHRI engines."""

from decimal import Decimal, ROUND_HALF_UP


def safe_div(num: float, den: float, fallback: float = 0.0) -> float:
    return num / den if den != 0 else fallback


def linear_interpolate(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    if x1 == x2:
        return y1
    return y1 + (y2 - y1) * safe_div(x - x1, x2 - x1)


def round_nearest_005(value: float) -> float:
    """Round a published AHRI rating to the nearest 0.05 using half-up."""
    step = Decimal("0.05")
    units = (Decimal(str(value)) / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return float(units * step)

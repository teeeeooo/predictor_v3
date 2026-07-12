"""Numeric primitives with identical semantics across extracted AHRI engines."""


def safe_div(num: float, den: float, fallback: float = 0.0) -> float:
    return num / den if den != 0 else fallback


def linear_interpolate(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    if x1 == x2:
        return y1
    return y1 + (y2 - y1) * safe_div(x - x1, x2 - x1)

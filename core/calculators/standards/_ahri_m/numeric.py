"""Small numeric primitives owned by Appendix M calculators."""

from decimal import Decimal, ROUND_HALF_UP


def safe_div(numerator: float, denominator: float, *, label: str) -> float:
    if denominator == 0:
        raise ValueError(f"{label} denominator must not be zero")
    return numerator / denominator


def linear_value(t: float, t1: float, v1: float, t2: float, v2: float) -> float:
    if t1 == t2:
        raise ValueError("linear interpolation temperatures must differ")
    return v1 + (v2 - v1) / (t2 - t1) * (t - t1)


def line_crossing(line, load_line, *, label: str) -> float:
    a_line = line(1.0) - line(0.0)
    a_load = load_line(1.0) - load_line(0.0)
    denominator = a_load - a_line
    if denominator == 0:
        raise ValueError(f"{label} lines do not have a unique crossing")
    return (line(0.0) - load_line(0.0)) / denominator


def lagrange_three(x: float, points: tuple[tuple[float, float], ...]) -> float:
    if len(points) != 3 or len({point[0] for point in points}) != 3:
        raise ValueError("quadratic interpolation requires three distinct x values")
    total = 0.0
    for index, (xi, yi) in enumerate(points):
        others = [points[j][0] for j in range(3) if j != index]
        total += yi * (x - others[0]) * (x - others[1]) / ((xi - others[0]) * (xi - others[1]))
    return total


def round_nearest_005(value: float) -> float:
    quantum = Decimal("0.05")
    scaled = (Decimal(str(value)) / quantum).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return float(scaled * quantum)

#!/usr/bin/env python3
"""Standalone ISO T1 PLF breakdown diagnostic.

This script intentionally does not import or call ISO16358Calculator.
It reproduces the current CSPF loop logic locally so per-bin intermediate
values can be inspected without adding prints to production code.
"""


CD = 0.25
T_100_LOAD = 35.0
T_0_LOAD = 20.0
REFERENCE_POINT = "35_full"

MEASURED_INPUTS = {
    "35_full": {"capacity": 2691.334, "power": 889.5},
    "35_half": {"capacity": 1249.055, "power": 303.2},
}

DERIVED_RULES = {
    "29_full": {
        "source": "35_full",
        "capacity_factor": 1.077,
        "power_factor": 0.914,
    },
    "29_half": {
        "source": "35_half",
        "capacity_factor": 1.077,
        "power_factor": 0.914,
    },
}

BIN_HOURS = [
    {"tj": 21, "nj": 100},
    {"tj": 22, "nj": 139},
    {"tj": 23, "nj": 165},
    {"tj": 24, "nj": 196},
    {"tj": 25, "nj": 210},
    {"tj": 26, "nj": 215},
    {"tj": 27, "nj": 210},
    {"tj": 28, "nj": 181},
    {"tj": 29, "nj": 150},
    {"tj": 30, "nj": 120},
    {"tj": 31, "nj": 75},
    {"tj": 32, "nj": 35},
    {"tj": 33, "nj": 11},
    {"tj": 34, "nj": 6},
    {"tj": 35, "nj": 4},
]


def resolve_points():
    resolved = {key: dict(value) for key, value in MEASURED_INPUTS.items()}
    for point_key, rule in DERIVED_RULES.items():
        source = resolved[rule["source"]]
        resolved[point_key] = {
            "capacity": source["capacity"] * rule["capacity_factor"],
            "power": source["power"] * rule["power_factor"],
        }
    return resolved


def point_parts(point_key):
    temp, load_type = point_key.split("_", 1)
    return float(temp), load_type


def interpolate_line(tj, low_temp, low_value, high_temp, high_value):
    if high_temp == low_temp:
        return low_value
    return low_value + (high_value - low_value) * (tj - low_temp) / (
        high_temp - low_temp
    )


def interpolate_at_tj(tj, resolved_points):
    grouped = {}
    for point_key, data in resolved_points.items():
        temp, load_type = point_parts(point_key)
        grouped.setdefault(load_type, []).append((temp, data["capacity"], data["power"]))

    interpolated = {}
    for load_type, points in grouped.items():
        points.sort(key=lambda item: item[0])
        lower = points[0]
        upper = points[-1]
        for index in range(len(points) - 1):
            left = points[index]
            right = points[index + 1]
            if left[0] <= tj <= right[0]:
                lower = left
                upper = right
                break
            if tj < points[0][0]:
                lower = points[0]
                upper = points[1]
                break
            if tj > points[-1][0]:
                lower = points[-2]
                upper = points[-1]
                break

        interpolated[load_type] = {
            "capacity": interpolate_line(tj, lower[0], lower[1], upper[0], upper[1]),
            "power": interpolate_line(tj, lower[0], lower[2], upper[0], upper[2]),
        }
    return interpolated


def calculate_row(tj, nj, resolved_points):
    l_c_ref = resolved_points[REFERENCE_POINT]["capacity"]
    delta_t = T_100_LOAD - T_0_LOAD
    lc = l_c_ref * (tj - T_0_LOAD) / delta_t

    interp_tj = interpolate_at_tj(tj, resolved_points)
    loads = [
        (data["capacity"], data["power"], load_type)
        for load_type, data in interp_tj.items()
    ]
    loads.sort(key=lambda item: item[0])

    lowest_cap, lowest_pow, _ = loads[0]
    highest_cap, highest_pow, _ = loads[-1]
    phi_ful = interp_tj["full"]["capacity"]

    x_engine = lc / lowest_cap if lowest_cap > 0 else 0.0
    x_iso = lc / phi_ful if phi_ful > 0 else 0.0

    if lc <= lowest_cap:
        mode = "CYCLE"
        plf_engine = max(1e-6, 1.0 - CD * (1.0 - x_engine))
        p_tj_engine = (x_engine * lowest_pow) / plf_engine if plf_engine > 0 else 0.0
    elif lc > highest_cap:
        mode = "INTERP"
        plf_engine = None
        p_tj_engine = highest_pow
    else:
        mode = "INTERP"
        plf_engine = None
        p_tj_engine = 0.0
        for index in range(len(loads) - 1):
            c1, p1, _ = loads[index]
            c2, p2, _ = loads[index + 1]
            if c1 < lc <= c2:
                if c2 == c1:
                    p_tj_engine = p1
                else:
                    p_tj_engine = p1 + (p2 - p1) * (lc - c1) / (c2 - c1)
                break

    return {
        "tj": tj,
        "mode": mode,
        "lc": lc,
        "lowest_cap": lowest_cap,
        "phi_ful": phi_ful,
        "x_engine": x_engine,
        "x_iso": x_iso,
        "plf_engine": plf_engine,
        "p_tj_engine": p_tj_engine,
        "nj": nj,
        "csec_contrib": p_tj_engine * nj,
    }


def fmt(value):
    if value is None:
        return "-"
    return f"{value:.6f}"


def main():
    resolved_points = resolve_points()
    rows = [
        calculate_row(float(row["tj"]), float(row["nj"]), resolved_points)
        for row in BIN_HOURS
    ]

    print(
        "tj | mode | Lc | lowest_cap(현재엔진) | phi_ful(tj) | "
        "X_engine | X_iso | PLF_engine | P_tj_engine | nj | "
        "CSEC_contrib(P_tj*nj)"
    )
    for row in rows:
        print(
            f"{row['tj']:.0f} | {row['mode']} | {fmt(row['lc'])} | "
            f"{fmt(row['lowest_cap'])} | {fmt(row['phi_ful'])} | "
            f"{fmt(row['x_engine'])} | {fmt(row['x_iso'])} | "
            f"{fmt(row['plf_engine'])} | {fmt(row['p_tj_engine'])} | "
            f"{row['nj']:.0f} | {fmt(row['csec_contrib'])}"
        )

    total_csec = sum(row["csec_contrib"] for row in rows)
    print(f"total_CSEC_Wh | {fmt(total_csec)}")


if __name__ == "__main__":
    main()

from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator


calc = AHRIHSPF2Calculator("data/usa_hspf2.json")

canonical_with_h42 = {
    "H12": (24000, 2200),
    "H32": (22000, 2100),
    "H42": (18000, 1900),
}

result = calc.calculate_hspf2_v3(canonical_with_h42)
bin_details = result["bin_details"]

print("HSPF2 v3 bin-level breakdown")
for row in bin_details:
    q_full = row["q_full"]
    building_load = row["building_load"]
    plr = building_load / q_full if q_full > 0 else None

    print(
        "bin={bin}, temp_F={temp_F}, bin_hour={hours}, "
        "building_load={building_load}, q_full={q_full}, "
        "p_full={p_full}, PLR={plr}, bin_energy={E_j}".format(
            bin=row["bin"],
            temp_F=row["temp_F"],
            hours=row["hours"],
            building_load=building_load,
            q_full=q_full,
            p_full=row["p_full"],
            plr=round(plr, 6) if plr is not None else None,
            E_j=row["E_j"],
        )
    )

for row in bin_details:
    bin_no = row["bin"]
    try:
        assert row["q_full"] >= 0
        assert row["p_full"] >= 0
        assert row["building_load"] >= 0
        assert row["E_j"] >= 0
    except AssertionError as exc:
        print(f"[FAIL] sanity check failed at bin {bin_no}: {row}")
        raise exc

print("[OK] sanity check pass")

capacity_lt_load_rows = [
    row for row in bin_details
    if row["q_full"] < row["building_load"]
]

if capacity_lt_load_rows:
    for row in capacity_lt_load_rows:
        print(
            "[경고] capacity < load 구간 발견: "
            f"bin {row['bin']}, temp={row['temp_F']}°F, "
            f"load={row['building_load']}, capacity={row['q_full']}, "
            f"case={row['case']}"
        )
else:
    print("[OK] 모든 bin에서 capacity >= load")

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from tests.helpers.iso16358_hspf_samples import OFFICIAL_GOLDEN_SAMPLE


ROOT = Path(__file__).resolve().parents[2]

EN_STANDBY = {
    "p_to": 0.0066,
    "p_sb": 0.0012,
    "p_ck": 0.01,
    "p_off": 0.01,
}
EN_SEER_POINTS = {
    "A": (3.6233, 0.847),
    "B": (2.4691, 0.389),
    "C": (1.5150, 0.137),
    "D": (1.1277, 0.062),
}


def ordered_result_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def en_scop_points(tbiv_temp_c: float, tol_temp_c: float) -> dict:
    return {
        "A": {"capacity": 2.1598, "power": 0.6062, "temp_c": -7},
        "B": {"capacity": 1.3293, "power": 0.2542, "temp_c": 2},
        "C": {"capacity": 0.9083, "power": 0.1540, "temp_c": 7},
        "D": {"capacity": 0.9299, "power": 0.1231, "temp_c": 12},
        "TOL": {
            "capacity": 2.3698,
            "power": 0.8067,
            "temp_c": tol_temp_c,
        },
        "Tbiv": {
            "capacity": 2.3669,
            "power": 0.7820,
            "temp_c": tbiv_temp_c,
        },
    }


def cspf_fixtures() -> dict:
    path = ROOT / "tests/fixtures/iso16358_cspf_golden_fixtures.json"
    return json.loads(path.read_text(encoding="utf-8"))["fixtures"]


def brazil_fixture() -> dict:
    path = ROOT / "tests/fixtures/brazil_cspf_compliance_golden.json"
    return json.loads(path.read_text(encoding="utf-8"))


def ks_official_hspf_input() -> dict:
    measured = copy.deepcopy(OFFICIAL_GOLDEN_SAMPLE)
    measured["rated_cooling_capacity"] = 3600.0
    return measured

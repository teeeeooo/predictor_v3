import json
from pathlib import Path


def test_ahri_2026_expected_overlay_keeps_raw_evidence_separate():
    path = Path(
        "tests/fixtures/ahri210240/official_calculator/2026_expected_overlay.json"
    )
    overlay = json.loads(path.read_text(encoding="utf-8"))

    assert overlay["schema_version"] == 1
    assert overlay["dual_stage_seer2_synthetic_01"]["status"] == "direct_m1"
    assert overlay["dual_stage_hspf2_synthetic_01"]["status"] == "recalculated_2026"
    assert overlay["triple_capacity_northern_hspf2_synthetic_01"]["status"].startswith(
        "partial_evidence"
    )

import json

import pandas as pd

from core.mapping import update as mapping_update
from core.mapping.condenser_identity import (
    canonical_condenser_pi,
    condenser_identity,
    condenser_requires_pi,
    condenser_spec_key,
)


def test_pfc_pi_is_always_absent_and_other_fin_types_require_pi():
    for stale_pi in ("PFC", "7", "stale", None):
        assert canonical_condenser_pi("PFC", stale_pi) == ""
        assert condenser_identity("ODU-A", "PFC", stale_pi, "1") == (
            "ODU-A",
            "PFC",
            "1",
        )
        assert condenser_spec_key("ODU-A", "PFC", stale_pi, "1") == "ODU-A PFC 1"

    assert not condenser_requires_pi("PFC")
    assert condenser_requires_pi("F&T")
    assert condenser_requires_pi("Future Fin")
    assert canonical_condenser_pi("Future Fin", "9") == "9"


def test_excel_converter_normalizes_pfc_pi_before_keys_and_options(
    tmp_path,
    monkeypatch,
):
    source = tmp_path / "mapping.xlsx"
    source.touch()
    destination = tmp_path / "data" / "mapping.json"
    odu_sheet = pd.DataFrame(
        [
            {
                "ODU": "ODU-A",
                "Fin type": "F&T",
                "Pi": "7",
                "Row": "1",
                "Cond Area": 10,
                "Cond Volume": 11,
            },
            {
                "ODU": "ODU-A",
                "Fin type": "PFC",
                "Pi": "PFC",
                "Row": "1",
                "Cond Area": 20,
                "Cond Volume": 21,
            },
            {
                "ODU": "ODU-A",
                "Fin type": "PFC",
                "Pi": "9",
                "Row": "2",
                "Cond Area": 30,
                "Cond Volume": 31,
            },
        ]
    )
    monkeypatch.setattr(
        mapping_update.pd,
        "read_excel",
        lambda *_args, **_kwargs: {"ODU": odu_sheet},
    )
    monkeypatch.setattr(mapping_update, "MAPPING_JSON_FILE", str(destination))

    mapping_update.update_mapping_to_json(str(source))

    mapping = json.loads(destination.read_text(encoding="utf-8"))
    assert mapping["odu_cascade"]["ODU-A"]["Available_Pis"] == ["7"]
    assert set(mapping["cond_specs"]) == {
        "ODU-A F&T 7 1",
        "ODU-A PFC 1",
        "ODU-A PFC 2",
    }
    assert "PFC" not in mapping.get("pi", {})
    assert "9" not in mapping.get("pi", {})

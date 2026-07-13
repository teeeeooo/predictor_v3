import json

import pandas as pd
import pytest

from core.mapping import update as mapping_update
from core.mapping.condenser_identity import (
    canonical_condenser_pi,
    condenser_identity,
    condenser_requires_pi,
    condenser_spec_key,
)
from core.mapping.update import MappingConversionError


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
            {
                "ODU": "ODU-A",
                "Fin type": "Future Fin",
                "Pi": "11",
                "Row": "3",
                "Cond Area": 40,
                "Cond Volume": 41,
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
    assert mapping["odu_cascade"]["ODU-A"]["Available_Pis"] == ["11", "7"]
    assert set(mapping["cond_specs"]) == {
        "ODU-A F&T 7 1",
        "ODU-A PFC 1",
        "ODU-A PFC 2",
        "ODU-A Future Fin 11 3",
    }
    assert "PFC" not in mapping.get("pi", {})
    assert "9" not in mapping.get("pi", {})


@pytest.mark.parametrize(
    ("fin_type", "pi", "row", "expected"),
    [
        ("F&T", "", "1", "Pi is required for Fin Type 'F&T'."),
        ("Future Fin", "", "1", "Pi is required for Fin Type 'Future Fin'."),
        ("", "7", "1", "Fin Type is required."),
        ("F&T", "7", "", "Row is required."),
    ],
)
def test_excel_converter_rejects_incomplete_condenser_rows_without_output(
    tmp_path,
    monkeypatch,
    fin_type,
    pi,
    row,
    expected,
):
    source = tmp_path / "mapping.xlsx"
    source.touch()
    destination = tmp_path / "data" / "mapping.json"
    odu_sheet = pd.DataFrame(
        [
            {
                "ODU": "ODU-A",
                "Fin type": fin_type,
                "Pi": pi,
                "Row": row,
                "Cond Area": 10,
                "Cond Volume": 11,
            }
        ]
    )
    monkeypatch.setattr(
        mapping_update.pd,
        "read_excel",
        lambda *_args, **_kwargs: {"ODU": odu_sheet},
    )
    monkeypatch.setattr(mapping_update, "MAPPING_JSON_FILE", str(destination))

    with pytest.raises(MappingConversionError) as caught:
        mapping_update.update_mapping_to_json(str(source))

    assert str(caught.value) == f"ODU sheet row 2: {expected}"
    assert not destination.exists()


def test_invalid_excel_conversion_preserves_existing_mapping(tmp_path, monkeypatch):
    source = tmp_path / "mapping.xlsx"
    source.touch()
    destination = tmp_path / "data" / "mapping.json"
    destination.parent.mkdir()
    destination.write_text('{"original": true}\n', encoding="utf-8")
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
                "ODU": "ODU-B",
                "Fin type": "Future Fin",
                "Pi": "",
                "Row": "1",
                "Cond Area": 20,
                "Cond Volume": 21,
            },
        ]
    )
    monkeypatch.setattr(
        mapping_update.pd,
        "read_excel",
        lambda *_args, **_kwargs: {"ODU": odu_sheet},
    )
    monkeypatch.setattr(mapping_update, "MAPPING_JSON_FILE", str(destination))

    with pytest.raises(MappingConversionError):
        mapping_update.update_mapping_to_json(str(source))

    assert json.loads(destination.read_text(encoding="utf-8")) == {"original": True}

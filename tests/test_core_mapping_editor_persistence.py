"""Mapping editor draft persistence tests."""

import json

from core.mapping.editor_persistence import (
    runtime_mapping_from_editor_draft,
    save_mapping_editor_draft,
)
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft


VALID_MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "evap_index": {"EVAP-A": {"Evap Area": 8.2, "Evap Volume": 2.1}},
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "compressor": {"CMP-A": {"Comp EER": 3.2, "Comp cc": 11}},
    "ref_type": {"R32": {}},
    "exp_type": {"EEV": {}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {"ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5}},
    "vendor_notes": {"keep": True},
}


def test_runtime_mapping_from_editor_draft_replaces_owned_and_preserves_unknown():
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)

    runtime = runtime_mapping_from_editor_draft(draft)

    assert runtime["vendor_notes"] == {"keep": True}
    assert runtime["ref_type"] == {"R32": {}}
    assert runtime["exp_type"] == {"EEV": {}}
    assert runtime["cond_specs"]["ODU-A F&T 7 1"] == {
        "Cond Area": 3.5,
        "Cond Volume": 4.5,
    }
    assert runtime["fin_type"] == {"F&T": {}}
    assert runtime["pi"] == {"7": {}}
    assert runtime["row"] == {"1": {}}


def test_runtime_mapping_from_editor_draft_uses_pfc_identity_without_pi():
    draft = project_runtime_mapping_to_editor_draft(
        {
            **VALID_MAPPING,
            "odu_cascade": {
                "ODU-A": {
                    "Available_Fins": ["PFC"],
                    "Available_Pis": [],
                    "Available_Rows": ["1"],
                }
            },
            "cond_specs": {"ODU-A PFC 1": {"Cond Area": 5, "Cond Volume": 6}},
        }
    )

    runtime = runtime_mapping_from_editor_draft(draft)

    assert runtime["cond_specs"] == {
        "ODU-A PFC 1": {"Cond Area": 5, "Cond Volume": 6}
    }
    assert runtime["odu_cascade"]["ODU-A"]["Available_Pis"] == []
    assert runtime["pi"] == {}


def test_valid_draft_saves_mapping_json_with_backup(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(json.dumps({"legacy": {"old": True}}), encoding="utf-8")
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)

    result = save_mapping_editor_draft(draft, mapping_file)

    saved = json.loads(mapping_file.read_text(encoding="utf-8"))
    assert result.success
    assert result.backup_path is not None
    assert result.backup_path.exists()
    assert saved["idu"]["IDU-A"]["ID Volume"] == 1.25
    assert saved["vendor_notes"] == {"keep": True}


def test_blocking_issue_prevents_save(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text('{"original": true}', encoding="utf-8")
    draft = project_runtime_mapping_to_editor_draft({**VALID_MAPPING, "ref_type": {}})

    result = save_mapping_editor_draft(draft, mapping_file)

    assert not result.success
    assert [issue.code for issue in result.issues] == ["required_section_missing"]
    assert json.loads(mapping_file.read_text(encoding="utf-8")) == {"original": True}


def test_save_failure_does_not_corrupt_original(tmp_path, monkeypatch):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text('{"original": true}', encoding="utf-8")
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)

    def fail_replace(_src, _dst):
        raise OSError("forced failure")

    monkeypatch.setattr("core.mapping.editor_persistence.os.replace", fail_replace)

    result = save_mapping_editor_draft(draft, mapping_file)

    assert not result.success
    assert json.loads(mapping_file.read_text(encoding="utf-8")) == {"original": True}

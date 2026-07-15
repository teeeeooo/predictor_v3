"""Mapping editor draft persistence tests."""

import json
from dataclasses import replace

from core.data_definition.model import MappingRequirement
from core.mapping.editor_commands import delete_draft_row, set_draft_cell
from core.mapping.editor_persistence import (
    runtime_mapping_from_editor_draft,
    save_mapping_editor_draft,
)
from core.mapping.editor_projection import (
    apply_mapping_requirements_to_editor_draft,
    project_runtime_mapping_to_editor_draft,
)


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


def test_runtime_projection_preserves_hidden_payload_for_every_owned_row_group(
    tmp_path,
):
    mapping = {
        **VALID_MAPPING,
        "idu": {"IDU-A": {"ID Volume": 1.25, "IDU Hidden": "keep-idu"}},
        "evap_index": {
            "EVAP-A": {
                "Evap Area": 8.2,
                "Evap Volume": 2.1,
                "Evap Hidden": "keep-evap",
            }
        },
        "odu": {"ODU-A": {"OD Volume": 2.5, "ODU Hidden": "keep-odu"}},
        "compressor": {
            "CMP-A": {
                "Comp EER": 3.2,
                "Comp cc": 11,
                "Comp Hidden": "keep-comp",
            }
        },
        "ref_type": {"R32": {"GWP": 675, "Ref Hidden": "keep-ref"}},
        "exp_type": {
            "EEV": {"Control Mode": "Electronic", "Exp Hidden": "keep-exp"}
        },
        "cond_specs": {
            "ODU-A F&T 7 1": {
                "Cond Area": 3.5,
                "Cond Volume": 4.5,
                "Cond Hidden": "keep-cond",
            }
        },
    }
    draft = project_runtime_mapping_to_editor_draft(mapping)
    draft = apply_mapping_requirements_to_editor_draft(
        draft,
        (
            MappingRequirement(
                column_key="gwp",
                ml_name="GWP",
                mapping_entity="ref_type",
                mapping_attribute="GWP",
                trigger_column="ref_type",
                data_type="number",
            ),
            MappingRequirement(
                column_key="control_mode",
                ml_name="Control Mode",
                mapping_entity="exp_type",
                mapping_attribute="Control Mode",
                trigger_column="exp_type",
            ),
        ),
    )
    for group, column, value in (
        ("idu", "ID Volume", "2.5"),
        ("evap_index", "Evap Area", "9.5"),
        ("odu", "OD Volume", "3.5"),
        ("compressor", "Comp EER", "4.2"),
        ("refrigerant", "GWP", "700.5"),
        ("expansion", "Control Mode", "Pulse"),
        ("odu_cond_specs", "Cond Area", "5.5"),
    ):
        draft = set_draft_cell(draft, group, 0, column, value)

    runtime = runtime_mapping_from_editor_draft(draft)

    assert runtime["idu"]["IDU-A"] == {
        "ID Volume": 2.5,
        "IDU Hidden": "keep-idu",
    }
    assert runtime["evap_index"]["EVAP-A"]["Evap Hidden"] == "keep-evap"
    assert runtime["evap_index"]["EVAP-A"]["Evap Area"] == 9.5
    assert runtime["odu"]["ODU-A"]["ODU Hidden"] == "keep-odu"
    assert runtime["compressor"]["CMP-A"]["Comp Hidden"] == "keep-comp"
    assert runtime["ref_type"]["R32"] == {
        "GWP": 700.5,
        "Ref Hidden": "keep-ref",
    }
    assert runtime["exp_type"]["EEV"] == {
        "Control Mode": "Pulse",
        "Exp Hidden": "keep-exp",
    }
    assert runtime["cond_specs"]["ODU-A F&T 7 1"] == {
        "Cond Area": 5.5,
        "Cond Volume": 4.5,
        "Cond Hidden": "keep-cond",
    }

    mapping_file = tmp_path / "mapping.json"
    result = save_mapping_editor_draft(draft, mapping_file)
    reloaded = project_runtime_mapping_to_editor_draft(
        json.loads(mapping_file.read_text(encoding="utf-8"))
    )

    assert result.success
    assert reloaded.group("idu").rows[0].value_for("IDU Hidden") == "keep-idu"
    assert (
        reloaded.group("odu_cond_specs").rows[0].value_for("Cond Hidden")
        == "keep-cond"
    )


def test_visible_blank_overlays_backing_value_instead_of_restoring_it():
    draft = project_runtime_mapping_to_editor_draft(
        {**VALID_MAPPING, "idu": {"IDU-A": {"ID Volume": 1.25, "Fan Size": 9}}}
    )
    draft = apply_mapping_requirements_to_editor_draft(
        draft,
        (
            MappingRequirement(
                column_key="fan_size",
                ml_name="Fan Size",
                mapping_entity="idu",
                mapping_attribute="Fan Size",
                trigger_column="idu",
                data_type="number",
                required=False,
            ),
        ),
    )
    draft = set_draft_cell(draft, "idu", 0, "Fan Size", "")

    runtime = runtime_mapping_from_editor_draft(draft)

    assert runtime["idu"]["IDU-A"]["Fan Size"] == ""


def test_key_rename_and_delete_keep_hidden_payload_owned_by_the_current_row():
    draft = project_runtime_mapping_to_editor_draft(
        {
            **VALID_MAPPING,
            "idu": {
                "IDU-A": {"ID Volume": 1.25, "Hidden": "row-a"},
                "IDU-B": {"ID Volume": 2.25, "Hidden": "row-b"},
            },
        }
    )
    draft = set_draft_cell(draft, "idu", 0, "IDU", "IDU-C")
    draft = delete_draft_row(draft, "idu", 1)

    runtime = runtime_mapping_from_editor_draft(draft)

    assert runtime["idu"] == {
        "IDU-C": {"ID Volume": 1.25, "Hidden": "row-a"}
    }


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


def test_runtime_mapping_normalizes_stale_pfc_pi_before_all_projections():
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
    group = draft.group("odu_cond_specs")
    stale_row = replace(
        group.rows[0],
        values={**group.rows[0].values, "Pi": "7"},
    )
    draft = replace(
        draft,
        groups=tuple(
            replace(group, rows=(stale_row,)) if item.group_key == group.group_key else item
            for item in draft.groups
        ),
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


def test_hidden_non_finite_payload_fails_save_without_replacing_original(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text('{"original": true}', encoding="utf-8")
    draft = project_runtime_mapping_to_editor_draft(
        {
            **VALID_MAPPING,
            "idu": {
                "IDU-A": {"ID Volume": 1.25, "Hidden Legacy Metric": float("nan")}
            },
        }
    )

    result = save_mapping_editor_draft(draft, mapping_file)

    assert not result.success
    assert "Out of range float values are not JSON compliant" in result.message
    assert json.loads(mapping_file.read_text(encoding="utf-8")) == {"original": True}

"""Mapping editor read-only snapshot export tests."""

import json

from core.mapping.editor_export import export_mapping_editor_snapshot_json
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft
from core.mapping.editor_validation import validate_mapping_editor_draft


MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "evap_index": {},
    "odu": {},
    "compressor": {},
    "ref_type": {"R32": {}},
    "exp_type": {"EEV": {}},
}


def test_json_snapshot_export_creates_read_only_review_file(tmp_path):
    draft = project_runtime_mapping_to_editor_draft(MAPPING)
    issues = validate_mapping_editor_draft(draft).issues
    export_file = tmp_path / "snapshot.json"

    result = export_mapping_editor_snapshot_json(draft, issues, export_file)

    payload = json.loads(export_file.read_text(encoding="utf-8"))
    assert result.success
    assert payload["snapshot_type"] == "mapping_editor_review_snapshot"
    assert payload["read_only"] is True
    assert payload["import_contract"] is False
    assert payload["groups"][0]["group"] == "IDU"
    assert payload["groups"][0]["rows"][0]["values"]["IDU"] == "IDU-A"
    assert payload["issues"] == []

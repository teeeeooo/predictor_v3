# Arc 14B Data Mapping Entity List Width Polish

## Goal

Fix the onscreen Data Mapping tab issue where the left `Entities` table started
too narrow and clipped entity key/label text.

## Modified Files

| File | Change |
| --- | --- |
| `apps/train/ui/data_mapping_panel.py` | Added entity panel minimum width and initial splitter size. |
| `tests/test_apps_train_data_mapping_ui_models.py` | Added a minimum-width guard to the panel construction test. |
| `result_reports/active/684_arc14b-data-mapping-entity-list-width-polish.md` | Added this report. |

## Verification

- `python3 -m py_compile apps/train/ui/data_mapping_panel.py`: OK
- `python3 -m pytest tests/test_apps_train_data_mapping_ui_models.py`: OK, 4 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py --verbose`: NG, pre-existing
  unrelated calculator raw hex literal plus existing LOC/code-map warnings. No
  changed file emitted a warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE,
  checked only; regeneration was not part of this polish.
- Onscreen smoke: OK. Data Mapping tab opened through System Events, and the
  `Entities` table now shows entity key/label/row/active columns at readable
  initial width.

## Manual Check

Manual onscreen check was performed. The `Notes` column may still truncate long
notes, but the entity identity columns are readable, which was the reported
issue.

## Known Risk

The local PySide6 app still exits with code 139 when the test window is closed.
This was also observed before this polish and did not block rendering or tab
interaction verification.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

- `reuse_commonization`: local-with-reason. The issue was specific to the
  Data Mapping split view initial sizing, so no common UI helper was extracted.
- `code_map_check`: checked; reference map is stale, but regeneration was not
  part of this polish.

Read Ledger:

- `apps/train/ui/data_mapping_panel.py`: lines 1-210, reason: target UI split view.
- `tests/test_apps_train_data_mapping_ui_models.py`: lines 1-95, reason: focused UI test.
- broad read: none.
- repeated read: none.

## Commit / Push

Final commit/push result will be reported in terminal output.

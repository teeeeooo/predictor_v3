# Data Mapping AX Crash Isolation And Model Guard

## Goal

Reduce `ReadOnlyMappingTableModel` risk during macOS Accessibility hierarchy reads, then isolate whether the Data Mapping crash is caused by the generic table model, table-heavy layouts, or the full `DataMappingPanel` composition.

## Scope

- Added defensive range checks to the read-only Data Mapping table model.
- Added tests for invalid, out-of-range, and ragged-row model access.
- Ran an incremental PySide6/Computer Use isolation spike from simple widgets to the full `DataMappingPanel`.

## Modified Files

- `apps/train/ui/data_mapping_models.py`
- `tests/test_apps_train_data_mapping_ui_models.py`

## Guard Change

- `data()` now returns `None` for invalid indexes, out-of-range rows/columns, and ragged-row cells.
- `headerData()` now returns `None` for unsupported roles/orientations and out-of-range horizontal/vertical sections.
- `flags()` now returns `Qt.NoItemFlags` for invalid or out-of-range cells.
- `cell_value()` now returns `None` for missing cells instead of using an empty string sentinel.

## Isolation Matrix

| Case | Surface | Computer Use Result |
| --- | --- | --- |
| A | label-only content | OK: tree, keyboard input, click |
| B | splitter with labels | OK: tree, keyboard input, click |
| C | nested frame sections | OK: tree, keyboard input, click |
| D | simple `QTableView` model | OK: tree, keyboard input, click |
| E | guarded `ReadOnlyMappingTableModel` table | OK: tree, keyboard input, click |
| F | multiple guarded mapping tables | OK: tree, keyboard input, click |
| G | splitter, disabled actions, multiple guarded tables | OK: tree, keyboard input, click |
| H | full `DataMappingPanel` with guarded model | NG: first Computer Use state captured a screenshot but returned an empty AX tree, then the process exited before click |

## Crash Stack

The H crash generated `Python-2026-07-04-003207.ips`. The triggered main-thread stack is still in the macOS Accessibility hierarchy path:

- `-[NSAccessibilityAttributeAccessorInfo getAttributeValue:forObject:]`
- `accessibilityArrayAttributeCount:`
- `__AXCopyAttributeValueForHierarchy`
- `_AXXMIGCopyHierarchy`

This matches the earlier Data Mapping crash shape and suggests the trigger is still full-panel AX hierarchy traversal, not the simple table model alone.

## Verification

- `python3 -m py_compile apps/train/ui/data_mapping_models.py`: OK
- `python3 -m pytest tests/test_apps_train_data_mapping_ui_models.py -q`: OK, 6 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py`: OK with existing unrelated LOC/class/code-map warnings
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked, stale reference map warning remains

## Findings

- The table model needed defensive guards because AX clients can ask invalid or stale indexes during hierarchy reads.
- The guarded model itself did not reproduce the crash in simple, multiple-table, or splitter-heavy isolation cases.
- The full `DataMappingPanel` still crashes on Computer Use state read, before a Computer Use click can be attempted.
- The likely remaining trigger is a full-panel composition or Qt/macOS AX interaction around that composition, not PredictWorkspace embedding, tab order, or the generic table model in isolation.

## Recommended GUI Smoke Policy

- Use focused Qt model tests and System Events / Qt programmatic smoke for Data Mapping until the full-panel AX crash is isolated further.
- Avoid Computer Use direct hierarchy/click smoke on the full Data Mapping panel as a required validation gate for now.
- Continue narrowing the full-panel composition by selectively disabling sections or replacing Data Mapping tables one group at a time.

## Excluded Scope

- No production UI layout overhaul.
- No service/controller/source provider changes.
- No dependency or Python/PySide version changes.
- No TrainShell, PredictWorkspace, or tab composition changes.

## Next Action

Continue with a DataMappingPanel composition isolation slice: disable or replace individual full-panel sections under a temporary harness to find the specific widget/section combination that makes `AXCopyHierarchy` crash.

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

## Read Ledger

- `AGENT_TASK_ROUTER.md`: UI, Smoke / Validation, Architecture, Result Report sections only.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: UI smoke and UX validation requirements.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: active report and commit/push workflow.
- `docs/WORK_PLAN.md`: current Arc 14B context.
- `apps/train/ui/data_mapping_models.py`: target model implementation.
- `tests/test_apps_train_data_mapping_ui_models.py`: focused UI model tests.
- Existing reports `683`, `684`, `686`, `689`: Data Mapping UI and prior Computer Use crash context.

## Commit / Push Note

Final commit/push result will be reported in terminal output.

# Data Mapping Panel Composition Slice Isolation

## Goal

Narrow the macOS Accessibility / Computer Use crash that reproduced only on the full `DataMappingPanel`, using actual panel components instead of synthetic lookalikes.

## Scope

- Built a temporary harness under `/tmp/datamapping_ax_slice` and removed it after the spike.
- Reused `DataMappingPanel`, its real table widgets, controller state DTOs, and `_apply_state()` path.
- Compared empty full layout, populated full layout, entities-only layout, selection-disabled layout, no-initial-selection layout, and the actual full standalone panel.
- Applied one small production guard after the trigger was isolated.

## Prior Findings

- Minimal PySide6 no-table and table apps accepted Computer Use state, keyboard, and click.
- Synthetic Data Mapping-like layouts with multiple guarded `QTableView` instances also passed.
- The old full `DataMappingPanel` crashed during Computer Use hierarchy reads with `NSAccessibilityAttributeAccessorInfo` / `AXCopyHierarchy` frames.

## Panel Path

- `DataMappingPanel.__init__()` creates command buttons, five `QTableView` surfaces, the splitter/body layout, then calls `refresh()`.
- `refresh()` calls the controller and passes `DataMappingControllerState` to `_apply_state()`.
- `_apply_state()` replaces the five table models, syncs disabled action buttons, and calls `_bind_entity_selection()`.
- The former `_bind_entity_selection()` path selected the current entity row immediately with `entity_table.selectRow(selected_row)`, then connected `currentRowChanged`.

## Slice Matrix

| Mode | Surface | Result |
| --- | --- | --- |
| S0 | Full panel layout, no auto refresh, empty models | OK: AX tree, keyboard, click |
| S1 | Full panel layout, fixed tiny populated state, initial entity selection | NG: AX tree empty, process crashed |
| S2 | Full panel + foundation sample controller state | Not separately run; covered by S13 actual full panel after the guard |
| S3 | Entities section only, populated state, initial entity selection | NG: AX tree empty, process crashed |
| S4 | Entities + attributes | Not run after S3/S10/S11 isolated the trigger |
| S5 | Entities + rows | Not run after S3/S10/S11 isolated the trigger |
| S6 | Entities + validation | Not run after S3/S10/S11 isolated the trigger |
| S7 | Entities + future actions | Not run after S3/S10/S11 isolated the trigger |
| S8 | Entities + attributes + rows | Not run after S3/S10/S11 isolated the trigger |
| S9 | Entities + attributes + rows + validation | Not run after S3/S10/S11 isolated the trigger |
| S10 | Full populated panel, selection binding disabled | OK: AX tree, keyboard, click |
| S11 | Full populated panel, signal connection kept, initial `selectRow()` skipped | OK: AX tree, keyboard, click |
| S12 | Full sections but no auto refresh | Not run; S0 covered no-auto empty and S1 covered manual populated apply |
| S13 | Actual full standalone panel after production guard | OK: AX tree, keyboard, click |

## Crash Stack Comparison

The S1 crash generated `Python-2026-07-05-132641.ips`.

Top-frame pattern matched previous crashes:

- `EXC_BAD_ACCESS` / `SIGSEGV`
- `-[NSAccessibilityAttributeAccessorInfo getAttributeValue:forObject:]`
- `accessibilityArrayAttributeCount:`
- `__AXCopyAttributeValueForHierarchy`
- `_AXXMIGCopyHierarchy`

## Narrowed Trigger

The smallest observed failing path was a populated `DataMappingPanel` entity table with initial `selectRow()` applied during `_bind_entity_selection()`.

The separating evidence:

- S0 full layout with empty tables passed.
- S1 full layout with tiny populated state and initial selection crashed.
- S3 entities-only populated state with initial selection crashed.
- S10 full populated state without selection binding passed.
- S11 full populated state with signal connection but without initial `selectRow()` passed.

This points to the initial selected-row accessibility state, not the foundation sample provider, PredictWorkspace, tab order, table model alone, or the non-entity detail sections.

## Production Changes

- Removed the initial `entity_table.selectRow(selected_row)` call from `_bind_entity_selection()`.
- Kept the `currentRowChanged` signal connection so user-driven entity selection can still refresh details.
- Added a focused test assertion that the panel does not force an initial current entity index after construction.

## Test Coverage

- `python3 -m py_compile apps/train/ui/data_mapping_panel.py apps/train/ui/data_mapping_models.py`: OK
- `python3 -m pytest tests/test_apps_train_data_mapping_ui_models.py -q`: OK, 6 passed
- Computer Use S13 after guard: OK for `get_app_state`, keyboard input, and click.

## Recommended GUI Smoke Policy

- Computer Use direct click is now usable for the standalone DataMappingPanel smoke path tested here.
- Computer Use `get_app_state` and keyboard are usable for this panel after the guard.
- Keep System Events named click or Qt programmatic smoke as the conservative fallback for TrainShell-wide checks until the full shell path is re-smoked.
- Arc 14B-2 can proceed; the next implementation slice can use focused tests plus a bounded DataMappingPanel Computer Use smoke when needed.

## Excluded Scope

- No runtime mapping repository adapter.
- No source provider change.
- No CSV v2 import/export.
- No mapping.json write/reload.
- No dependency, Python, PySide6, or Qt version change.
- No broad layout/UX rewrite.

## Structure

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:
- `AGENT_TASK_ROUTER.md`: Result Report, UI, and Smoke / Validation sections only.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: UI table/window validation guidance.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: report numbering and commit/push rules.
- `docs/WORK_PLAN.md`: Arc 14B next action context.
- `apps/train/ui/data_mapping_panel.py`: constructor, refresh, `_apply_state()`, `_bind_entity_selection()`.
- `apps/train/ui/data_mapping_view_models.py`: table row projection helpers.
- `apps/train/controllers/data_mapping_controller.py`: controller state path.
- `apps/train/services/data_mapping_service.py`: foundation sample provider summary.
- Reports `686`, `689`, `690`: prior Data Mapping / Computer Use crash evidence.

## Next Action

Proceed with Arc 14B-2 Data Mapping runtime mapping repository read adapter. Re-smoke the Data Mapping tab in the full TrainShell once the next slice touches the shell or data source path.

## Commit / Push Note

Final commit/push result will be reported in terminal output.

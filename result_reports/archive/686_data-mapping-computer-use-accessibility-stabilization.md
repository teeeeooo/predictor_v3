# Data Mapping Computer Use Accessibility Stabilization

## Goal

Apply a narrow Data Mapping Manager UI stabilization pass for Computer Use GUI
smoke crashes: reduce table state churn during refresh, make accessibility
nodes easier to identify, and widen the entity pane.

## Scope

- Stabilized `DataMappingPanel._apply_state()` by blocking table signals while
  replacing table models and rebinding row selection.
- Blocked selection-model signals while selecting the current entity row, then
  connected `currentRowChanged` after the selection state settled.
- Added accessible names/object names for the panel, splitter, tables, labels,
  and command buttons.
- Increased the entity pane minimum width and splitter initial detail width.
- Added a focused UI model test assertion for the accessibility labels and
  entity width floor.

## Non-goals

- No Data Mapping CRUD, CSV v2 import/export, mapping.json write/reload, or
  runtime cascade behavior was added.
- No Train/Predict shell merge, Predict schema behavior, model artifact, or
  mapping runtime owner behavior changed.
- This does not claim to fully fix the Computer Use crash.

## Verification

- `python3 -m py_compile apps/train/ui/data_mapping_panel.py`: OK
- `python3 -m pytest tests/test_apps_train_data_mapping_ui_models.py`: OK
  (`4 passed`)
- `git diff --check`: OK
- `python3 -B tools/code_checker/build_reference_map.py --check`: NG/stale,
  existing code map fingerprint/HEAD mismatch; not regenerated for this narrow
  UI stabilization.
- `python3 -B tools/check_code_structure.py --verbose`: OK with warnings only;
  warnings are existing unrelated calculator/standard LOC/class warnings plus
  stale code-map reminder. No changed Data Mapping file emitted a structure
  warning.
- Computer Use onscreen smoke after this change: NG. Clicking the Train/Admin
  Data Mapping tab still quit the Python app with SIGSEGV.

## Crash Evidence

Latest observed crash report:
`~/Library/Logs/DiagnosticReports/Python-2026-07-03-233035.ips`.

The faulting thread is the main thread inside AppKit accessibility hierarchy
copy. The top frames include `NSAccessibilityAttributeAccessorInfo`,
`accessibilityArrayAttributeCount`, `__AXCopyAttributeValueForHierarchy`, and
`_AXXMIGCopyHierarchy`, followed by the AppKit/Qt event loop. This supports the
current working diagnosis that the remaining crash is in the macOS/AppKit/Qt
accessibility bridge during Computer Use hierarchy reads, not a Python
exception thrown by the Data Mapping panel.

## Table / UI Parity

- Existing owner reused: `DataMappingPanel` remains a read-only Qt table
  surface backed by `QTableView` and `ReadOnlyMappingTableModel`.
- No `QTableWidget` or `setCellWidget()` was introduced.
- Spreadsheet parity remains intentionally limited because this surface is
  read-only foundation UI; editable copy/paste/undo semantics belong to a later
  CRUD/import slice.
- Accessibility naming is now explicit for the table surfaces so external UI
  inspection can target stable nodes.

## Structure

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:
- `AGENT_TASK_ROUTER.md`: lines 124-190 and 294-320, reason: Result Report and
  UI route gates.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: lines 1-160, reason: table UI
  source workflow and validation requirements.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: lines 1-220, reason:
  report numbering, validation, commit/push rules.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 1-160, reason: staged
  report association and structured change gate.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`: lines 1-180, reason: table
  surface parity trigger.
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`: lines 1-180, reason: Qt
  table implementation and signal blocking discipline.
- `apps/train/ui/data_mapping_panel.py`: lines 1-253, reason: target UI
  surface and edited state/selection lifecycle.
- `tests/test_apps_train_data_mapping_ui_models.py`: lines 1-91, reason:
  focused UI model/panel assertions.
- `~/Library/Logs/DiagnosticReports/Python-2026-07-03-233035.ips`: focused
  crash frame search, reason: Computer Use crash evidence.
- broad read: none.
- repeated read: none.

## Known Risks

- Computer Use can still crash the Python/Qt app while reading the macOS
  accessibility hierarchy. The current patch reduces Data Mapping table churn
  but does not remove the underlying AppKit/Qt accessibility failure.
- Further work should investigate a higher-level workaround, such as a
  non-AX GUI smoke path, a narrower accessibility tree, or Qt accessibility
  bridge mitigation if available.

## Commit / Push

This report is committed with the source and test changes. Final commit hash,
push result, remote main match, and final status are reported in terminal
output to avoid a self-referential report hash update loop.

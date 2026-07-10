# 559 - Arc 9.5 Predict Table Parity Slice

## Goal

Move Predict input/result tables closer to spreadsheet-like visual and
interaction parity while preserving the existing schema, mapping, controller,
and service boundaries.

## Changes

- Added `apps/predict/ui/tables/clipboard.py`:
  - TSV parse/format helpers;
  - CRLF/CR/LF normalization;
  - trailing newline handling;
  - rectangular selection bounds helper.
- Added `apps/predict/ui/tables/delegates.py`:
  - dropdown affordance painting;
  - one-click combo popup;
  - combo editor data/model binding.
- Updated input/result table views:
  - cell selection instead of row-only selection;
  - Ctrl+C copy as TSV;
  - input Ctrl+V paste anchored at current/top-left selection;
  - input Delete/Backspace clear editable cells only;
  - result table copy support.
- Updated table models:
  - schema column descriptors exposed for width/delegate setup;
  - input/auto/result background roles use the PySide6 style adapter;
  - invalid numeric ML-feature cells render validation background/tooltips;
  - idempotent input edits return without controller/noisy refresh work;
  - result cells stay selectable/copyable and mutation-protected.
- Updated `PredictWorkspace`:
  - schema width application;
  - row-height baseline;
  - fallback dropdown options for `ref_type` and `exp_type`;
  - command-bar Paste and Copy Results buttons wired to clipboard helpers;
  - Export remains a controlled disabled placeholder.
- Added `tests/test_apps_predict_table_interactions.py`.

## UI/UX Contract Check

Corrected in this slice:

- TSV copy selected rectangle.
- TSV paste anchored at current/top-left selection.
- CRLF/CR/LF normalization.
- Trailing newline handling.
- Out-of-bounds paste drop behavior.
- Delete/Backspace clear editable cells only.
- Read-only/result cells copyable but mutation-protected.
- Row header remains user-facing row identity; no visible `case_id` column.
- Input/auto/result visual distinction improved.
- Dropdown affordance and one-click popup foundation added.
- Invalid numeric rendering added for numeric ML-feature cells.

Intentionally deferred:

- Grouped undo for edit/paste/clear.
- Tab / Shift+Tab / Enter / Shift+Enter navigation override.
- Full click/type replace-on-type state machine.
- Mapping-backed per-row dropdown option updates beyond safe fallback options.

Remaining gap:

- PySide6-specific table adapter is still not a fully documented reusable
  adapter. This slice uses `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
  directly as the acceptance contract and records the deferred parity items
  above.

## Boundary Decision

Table views own user interaction mechanics. Table models expose cell values,
editability, and validation state, but do not call the mapping repository,
prediction service, training execution, or calculator logic. Mapping/autofill
continues through `InputEditController`.

## Excluded Scope

- No worker/progress/cancel.
- No Trainer execution.
- No ML algorithm, feature list, preprocessing formula, model artifact, mapping
  JSON schema, calculator formula/config/fixture/golden, or public result
  contract changes.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py apps/common/**/*.py`: passed.
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.predict.ui.workspace import PredictWorkspace; w=PredictWorkspace(); assert w is not None; assert w.command_bar.paste_button.isEnabled(); assert w.command_bar.copy_results_button.isEnabled()"`: passed.
- `python3 -B -m pytest tests -k "predict and (table or clipboard or schema or mapping)"`: 20 passed.
- `rg -n "PyQt5|from ui\\.|import ui\\." apps core tests scripts docs ui_common --glob "!result_reports/archive/**" --glob "!docs/archive/**"`: no matches.
- `git diff --check`: passed.
- `git status --short`: checked before closeout.

Note: offscreen smoke still emits the existing Qt font alias warning for the
environment; it does not block widget construction.

## Next

Slice 5 - Predict mapping / validation / result status visual integration.

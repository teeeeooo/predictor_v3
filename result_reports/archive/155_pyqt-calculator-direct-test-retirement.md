# 155 - PyQt Calculator Direct Test Retirement

## Goal

Retire only the PyQt calculator-only direct tests identified by report 154,
while leaving calculator source, Predict/Train PyQt paths, shared or uncertain
PyQt tests, and environment support policy unchanged.

## Scope

- Reconfirm ownership of the three candidate direct test files.
- Delete only candidates confirmed to protect calculator-only source.
- Preserve mixed/shared utility tests and PyQt environment guard tests.
- Record the completed retirement slice and next decision order in
  `docs/WORK_PLAN.md`.

## Non-goals

- No PyQt calculator source, import, Predict/Train, shared utility, Tkinter,
  core calculator, profile, dispatcher, fixture, skip marker, or xfail marker
  changes.
- No updates to `project_log.md`, `ACTIVE_DOCUMENTS.md`,
  `result_reports/memory/project_memory_seed.md`,
  `docs/guides/pyqt_test_support_matrix.md`, architecture docs, or result
  report lifecycle state.

## Project Memory Recall Gate

Keyword-limited searches in `result_reports/memory/project_memory_seed.md`
confirmed the evidence that:

- PyQt calculator-only packaging/UI is on hold while the Tkinter calculator
  direction is evaluated.
- PyQt Predict/Train applications remain retention candidates while
  calculator-only PyQt assets were to be audited for retirement.
- The project-wide code quality gate requires the structure guard for
  structure-affecting work.

The seed did not contain a direct-test retirement conclusion. The required
decision was therefore checked against the current source/test references and
the scoped R1 recommendation in
`result_reports/active/154_pyqt-calculator-retirement-audit.md`. The memory
seed is evidence only and was not modified.

## Task 1 - Target Test Inventory

| Candidate test | Direct protected source | Shared or retained surface check | Judgment basis |
| --- | --- | --- | --- |
| `tests/test_app_calculator_ui_smoke.py` | `ui/calc_window.py::CalculatorWindow` and its AHRI/EN/validation wiring | It asserted `SpreadsheetTableView` only through `CalculatorWindow` wiring; it did not exercise independent shared utility behavior or Predict/Train | calculator-only direct test |
| `tests/test_iso16358_result_table_copy_tsv.py` | `ui/calculators_2point.py` read-only models/views (`TwoPointTableModel`, `RegionResultTableModel`, `TraceTableModel`, `RegionDetailTab`, `ReadOnlyCopyTableView`) | No import of `ui.spreadsheet_table`, `ui.theme`, Predict, or Train surface | calculator-only direct test |
| `tests/test_calculator_errors.py` | `ui/calculator_errors.py` parser, validation exception, style/reset and input helpers | One assertion consumed `ui.theme.color` only to verify calculator error styling; independent token-registry protection remains in `tests/test_ui_theme_tokens.py` | calculator-only direct test |

The target tests protected `ui/calc_window.py`,
`ui/calculators_2point.py`, and `ui/calculator_errors.py`, which report 154
classified as calculator-only source retirement candidates. None directly
protects `app_predict.py`, `app_train.py`, or their UI dependencies.

## Task 2 - Retire / Hold / Keep Decision

### Retire now

- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_calculator_errors.py`

Each file directly protected a calculator-only source module and did not own
retained Predict/Train or independent shared-utility behavior.

### Hold

- `tests/test_iso16358_table_excel_like_behavior.py`: imports
  `ui.calculators_2point.ProfileInputGrid*` together with helper symbols from
  `ui.spreadsheet_table`; retain until shared utility retention is decided.
- `tests/test_spreadsheet_table_model.py`
- `tests/test_spreadsheet_table_view.py`
- `tests/test_ui_theme_tokens.py`

The last three remain the explicit independent protection for the
shared/uncertain `ui/spreadsheet_table.py` and `ui/theme.py` surfaces.

### Keep

- `tests/helpers/pyqt_env.py`
- `tests/test_pyqt_environment_guard.py`

The skip helper is still consumed by retained
`tests/test_iso16358_table_excel_like_behavior.py` and
`tests/test_spreadsheet_table_view.py`; environment policy remains active.

## Task 3 - Removed Tests And Deliberate Non-Changes

### Deleted files

- `tests/test_app_calculator_ui_smoke.py`
- `tests/test_iso16358_result_table_copy_tsv.py`
- `tests/test_calculator_errors.py`

### Retained files

- `tests/test_iso16358_table_excel_like_behavior.py`
- `tests/test_spreadsheet_table_model.py`
- `tests/test_spreadsheet_table_view.py`
- `tests/test_ui_theme_tokens.py`
- `tests/helpers/pyqt_env.py`
- `tests/test_pyqt_environment_guard.py`

### Why source/import cleanup is excluded

This is test retirement before source retirement. The source candidates
`app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`, and
`ui/calculator_errors.py` remain present for the separately ordered source
retirement slice. Removing imports or source now would merge the R1 and R3
decisions and exceed the authorized scope.

Reference searches after deletion show expected historical/active-document
mentions of the removed tests, including
`docs/guides/pyqt_test_support_matrix.md`. That guide is explicitly excluded
from this slice and is a candidate for the later guide update/retirement
decision.

## Task 4 - Work Plan Update

`docs/WORK_PLAN.md` now records:

- retirement of the three direct calculator-only tests;
- continued hold/retention of mixed/shared tests and PyQt environment guards;
- next recommended action order:
  1. shared PyQt utility retention decision for `ui/spreadsheet_table.py`,
     `ui/theme.py`, and their remaining tests;
  2. PyQt calculator-only source retirement;
  3. PyQt calculator-only active docs update;
  4. PyQt support matrix guide update or retirement judgment.

`ACTIVE_DOCUMENTS.md`, `project_log.md`, and the memory seed were not modified,
as required by scope.

## Task 5 - Report And Lifecycle

This report captures the R1 implementation result and a single memory-delta
candidate. Result report lifecycle maintenance is excluded because the task
authorizes a new active report only; it does not authorize summary creation,
active/archive movement, or memory seed synchronization.

## Task 6 - Verification

- `python3 -B tools/check_code_structure.py`:
  `code structure guard: OK (no findings)`.
- Remaining shared/held PyQt test run:
  `python3 -B -m pytest tests/test_iso16358_table_excel_like_behavior.py tests/test_spreadsheet_table_model.py tests/test_spreadsheet_table_view.py tests/test_ui_theme_tokens.py tests/test_pyqt_environment_guard.py -q -rxXs`
  completed with `95 passed, 31 skipped`. The skips are the retained known-bad
  macOS Python 3.14 + PyQt5 guarded widget tests.
- Full suite:
  `python3 -B -m pytest -q -rxXs` completed with
  `566 passed, 32 skipped, 19 xfailed in 1.82s`.
- Baseline delta against `585 passed, 59 skipped, 19 xfailed`:
  `-19 passed`, `-27 skipped`, `0 xfailed`. This matches deletion of
  `tests/test_calculator_errors.py` passing cases and the two direct widget
  files whose cases were skipped on the known-bad local host.
- No native abort occurred in targeted or full-suite execution.

## Changed Files

- `tests/test_app_calculator_ui_smoke.py` - deleted direct calculator window
  coverage.
- `tests/test_iso16358_result_table_copy_tsv.py` - deleted direct
  `ui.calculators_2point` read-only table coverage.
- `tests/test_calculator_errors.py` - deleted direct calculator error-helper
  coverage.
- `docs/WORK_PLAN.md` - records R1 completion and next ordered decisions.
- `result_reports/active/155_pyqt-calculator-direct-test-retirement.md` -
  records the implementation evidence and verification.

## Known Failures / Risks

- Calculator-only source remains present without the retired direct regression
  tests until a separately authorized source-retirement decision is executed.
- Active docs that enumerate the deleted PyQt widget tests are intentionally
  stale after this narrowly scoped test-removal slice; they require the later
  active-doc/support-matrix update decision.
- Mixed/shared tests have been retained, so `ui/spreadsheet_table.py`,
  `ui/theme.py`, and PyQt environment guard disposition is still intentionally
  unresolved.

## Scope Compliance

- No source or import file was modified or deleted.
- No shared/uncertain test, environment helper, support matrix guide,
  Predict/Train path, Tkinter path, core/profile/dispatcher, marker, fixture,
  expected value, project log, active documents index, or memory seed was
  modified.
- No report lifecycle move or maintenance was performed.

## Commit / Push

Source/runtime change: none; authorized test retirement plus
`docs/WORK_PLAN.md` and this result report only.

- Test/docs commit: `d2e94be` (`test: retire PyQt calculator direct tests`)
- Report commit: this report is committed separately after finalization.
- Push: both commits are pushed together to `origin/work/ui-ux-ssot-adoption`
  after the report commit.

## Project Memory Delta

```yaml
- type: decision
  topic: pyqt-calculator-direct-test-retirement
  content: "PyQt calculator-only direct tests were retired before source retirement, while mixed/shared PyQt utility tests and environment guard tests remain held for a separate retention decision."
  keywords:
    - PyQt calculator
    - direct tests
    - retirement
    - shared utility
  assertionStatus: observed
  source: result_reports/active/155_pyqt-calculator-direct-test-retirement.md (Task 2 - Retire / Hold / Keep Decision)
```

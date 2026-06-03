# 156 - Shared PyQt Utility Retention Decision

## Goal

Decide whether the shared/uncertain PyQt utilities and supporting test-policy
assets held in reports 154 and 155 should survive PyQt calculator-only source
retirement, without executing any source or test retirement in this task.

## Scope

- Inventory current runtime, test, and active-document ownership for
  `ui/spreadsheet_table.py`, `ui/theme.py`, retained PyQt tests, the PyQt
  environment guard, and the support matrix guide.
- Record retention/hold/split decisions and narrowly ordered follow-up slices.
- Update `docs/WORK_PLAN.md` with the decision and next prerequisite.

## Non-goals

- No deletion, move, rename, source/test/import/marker/fixture change, PyQt
  calculator source retirement, support-matrix edit, architecture edit,
  Predict/Train change, Tkinter implementation, or packaging work.
- No update to `project_log.md`, `ACTIVE_DOCUMENTS.md`, or
  `result_reports/memory/project_memory_seed.md`.
- No result-report lifecycle maintenance.

## Project Memory Recall Gate

Keyword-limited searches of `result_reports/memory/project_memory_seed.md`
found the established direction that PyQt calculator-only packaging/UI is on
hold while Tkinter is evaluated, and that PyQt Predict/Train remains a
retention candidate while calculator-only assets undergo retirement audit.

The seed does not yet contain the 155 direct-test retirement result or a shared
utility retention conclusion. Current evidence was therefore drawn from
reports 154/155, current imports/tests, and active UI/UX owner docs. The seed
was treated as evidence only and was not modified.

## Task 1 - Ownership Inventory

### Runtime imports

| Asset | Current runtime imports found | Classification |
| --- | --- | --- |
| `ui/spreadsheet_table.py` | imported by `ui/calc_window.py` and `ui/calculators_2point.py`; no direct import from Predict/Train or `ui_tk/` | calculator-runtime dependency today; future/shared PyQt utility candidate |
| `ui/theme.py` | imported by `ui/calc_window.py` and `ui/calculator_errors.py`; no direct import from Predict/Train or `ui_tk/` | calculator-runtime dependency today; future/shared token utility candidate |
| `tests/helpers/pyqt_env.py` | imported by retained widget tests `tests/test_iso16358_table_excel_like_behavior.py` and `tests/test_spreadsheet_table_view.py`, and tested by `tests/test_pyqt_environment_guard.py` | test-only environment utility |

`app_predict.py`, `app_train.py`, `ui/predict_window.py`, `ui/train_window.py`,
`ui/base_model.py`, `ui/base_view.py`, and `ui_tk/` do not directly import the
two held utility modules in the current tree.

### Code/test shape

- `ui/spreadsheet_table.py` identifies itself as reusable spreadsheet-like
  table model/helpers for PyQt UIs. It includes pure helpers
  (`parse_tsv`, `format_tsv`, `points_from_grid`), general
  `SpreadsheetTableModel`/`SpreadsheetTableView`, and calculator-oriented
  AHRI/EN factory helpers in the same module.
- `ui/theme.py` is a small PyQt-independent color/font/spacing token registry;
  it is importable without PyQt5.
- `tests/test_spreadsheet_table_model.py` covers generic table operations and
  signals as well as AHRI/EN table factories.
- `tests/test_spreadsheet_table_view.py` covers generic spreadsheet view
  keyboard/clipboard behavior.
- `tests/test_ui_theme_tokens.py` protects the token registry independently of
  any calculator source and explicitly checks PyQt-free importability.

### Active document ownership

- `docs/ui_ux/00_UI_UX_SYSTEM.md` is the common UI/UX SSOT and points to
  toolkit adapters.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` defines token names as a
  contract and expects projects to bind them in a theme module.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` owns shared
  spreadsheet-like behavior across toolkit implementations.
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md` is the active PyQt
  implementation contract for every selected PyQt table surface.
- `ACTIVE_DOCUMENTS.md` registers these documents as active owners for table
  surfaces including calculator, Train/Predict, helpers, and fixtures.

The active docs express a reusable contract, but they do not prove a current
non-calculator runtime consumer of these two source files. This distinction is
why the decision is hold rather than unconditional active-runtime retention.

## Task 2 - Related Test Owner Policy

| File | Protected surface | Decision | Reason |
| --- | --- | --- | --- |
| `tests/test_spreadsheet_table_model.py` | generic model/helpers/signals plus calculator-specific factories within `ui.spreadsheet_table.py` | **keep while utility is held** | preserves reusable component evidence; factory subset can be reconsidered only with source disposition |
| `tests/test_spreadsheet_table_view.py` | generic `SpreadsheetTableView` clipboard/clear/undo/navigation behavior | **keep** | protects the future/shared PyQt table behavior and still requires widget environment guard |
| `tests/test_ui_theme_tokens.py` | PyQt-independent token registry contract | **keep** | protects shared token concept independently of retired calculator direct tests |
| `tests/test_iso16358_table_excel_like_behavior.py` | `ui.calculators_2point.ProfileInputGrid*` plus helpers imported from `ui.spreadsheet_table` | **split needed before calculator source retirement** | calculator-only widget ownership and shared helper assertions are mixed in one test file |
| `tests/helpers/pyqt_env.py` | known-bad host skip policy used by retained widget tests | **keep** | still has live consumers |
| `tests/test_pyqt_environment_guard.py` | correctness of the environment skip policy | **keep** | policy remains required while guarded PyQt widget tests remain |

`tests/test_iso16358_table_excel_like_behavior.py` imports the calculator model
and view and uses the shared table helpers/constants in the same test module.
It is not eligible for wholesale retirement in the calculator source slice
without first splitting reusable assertions or deciding that they are fully
covered elsewhere.

## Task 3 - Retention Decisions

### `ui/spreadsheet_table.py`

**Decision: C - quarantine/hold until a future PyQt surface needs it or a
focused split decision is approved.**

Evidence:

- No current Predict/Train or Tkinter runtime consumer was found; current
  runtime imports originate in calculator source slated for later retirement.
- The module contains generally reusable model/view/TSV behavior and has
  independent regression tests.
- The same file also contains AHRI/EN calculator factory helpers, so declaring
  all of it a permanent shared runtime dependency would overstate the current
  ownership evidence.
- Active UI/UX contracts retain PyQt table behavior as an allowed/owned future
  surface and Predict/Train remains a PyQt retention candidate.

Implication: do not remove this module with calculator-only source. Preserve it
and its generic tests until a later usage or decomposition decision; a later
split can separate reusable model/view/helpers from calculator-specific
factories if needed.

### `ui/theme.py`

**Decision: C - quarantine/hold until a future PyQt UI token reuse decision.**

Evidence:

- Runtime imports presently arise only through calculator source.
- The module is PyQt-independent and implements token names governed by the
  active design-token contract.
- `tests/test_ui_theme_tokens.py` is independent of calculator source and
  verifies framework-free import and token integrity.

Implication: do not delete it with calculator source. Retain it and its test as
a low-cost token-foundation hold asset. A move to a more framework-neutral
location is possible only as a separate later design task, not a retirement
prerequisite.

### PyQt environment guard

**Decision: A - keep while any PyQt widget tests remain.**

Evidence:

- Retained `tests/test_iso16358_table_excel_like_behavior.py` and
  `tests/test_spreadsheet_table_view.py` still apply
  `macos_python314_pyqt5_known_bad_skip_mark()`.
- Report 155 verified these retained tests complete without native abort under
  the guard.

Implication: keep both `tests/helpers/pyqt_env.py` and
`tests/test_pyqt_environment_guard.py`. Retiring calculator-only source does
not retire the guard while any retained widget test remains.

### PyQt support matrix guide

**Decision: A - keep and narrow later.**

Evidence:

- The guide is stale for the already deleted direct test entries and baseline,
  but still owns the known-bad environment rationale and commands/policy for
  retained guarded widget tests.
- `ACTIVE_DOCUMENTS.md` registers it as the PyQt widget support/skip matrix.

Implication: do not delete the guide. Update/narrow its test inventory and
baseline in a separate docs slice after the mixed-test/source decision is
settled, or earlier as a narrowly scoped documentation correction if desired.

## Task 4 - Follow-up Slices

### Slice S1 - Mixed ISO Table Test Split Or Retirement

- **Purpose:** remove the blocker between calculator source retirement and
  retained shared table coverage.
- **Target files:** `tests/test_iso16358_table_excel_like_behavior.py`;
  reference only `ui/calculators_2point.py` and `ui/spreadsheet_table.py`.
- **Included scope:** classify or separate calculator-owned
  `ProfileInputGrid*` coverage from any reusable helper assertions; retire only
  the calculator-owned portion if authorized.
- **Excluded scope:** utility source deletion, calculator source deletion,
  support matrix updates, marker-policy changes.
- **Prerequisites:** this decision report.
- **Verification:** targeted retained table tests and full suite, with expected
  skip/pass delta recorded.

### Slice S2 - Shared PyQt Utility Hold Status Documentation

- **Purpose:** align active status wording with the hold decision.
- **Target files:** applicable status/design docs only if expressly approved;
  at minimum evaluate `docs/WORK_PLAN.md` status already recorded here.
- **Included scope:** clarify that reusable source is held rather than a
  calculator retirement candidate.
- **Excluded scope:** source/test changes and historical report rewrites.
- **Prerequisites:** none beyond this decision; can be combined with a later
  active-doc slice only if scope remains documentation-only.
- **Verification:** targeted reference search.

### Slice S3 - PyQt Calculator-Only Source Retirement

- **Purpose:** retire calculator-only PyQt source without removing held shared
  utility or retained PyQt paths.
- **Target files:** `app_calculator.py`, `ui/calc_window.py`,
  `ui/calculators_2point.py`, `ui/calculator_errors.py`; any necessary
  calculator-only entry references authorized in that slice.
- **Included scope:** calculator-only source retirement after S1.
- **Excluded scope:** `ui/spreadsheet_table.py`, `ui/theme.py`, Predict/Train,
  shared/environment tests, Tkinter feature work.
- **Prerequisites:** S1 complete; explicit deletion approval.
- **Verification:** structure guard, retained entrypoint import/smoke as
  appropriate, retained shared tests, full suite.

### Slice S4 - PyQt Calculator-Only Active Docs Update

- **Purpose:** remove active claims about retired calculator source after S3.
- **Target files:** `README.md`, `project_brief.md`, `docs/WORK_PLAN.md`, and
  specifically approved current-state architecture/design/status passages.
- **Included scope:** current active references only.
- **Excluded scope:** historical reports/archive rewrites and support policy
  guide unless separately included in S5.
- **Prerequisites:** S3 completion.
- **Verification:** `rg` against retired source names with historical matches
  classified separately.

### Slice S5 - PyQt Support Matrix Guide Narrowing

- **Purpose:** retain the environment-policy guide while matching it to
  surviving guarded PyQt widget tests and current baseline.
- **Target files:** `docs/guides/pyqt_test_support_matrix.md`;
  `ACTIVE_DOCUMENTS.md` only if ownership/status actually changes.
- **Included scope:** remove retired direct-test inventory, update commands and
  baseline, retain known-bad policy rationale.
- **Excluded scope:** skip-helper behavior changes or source retirement.
- **Prerequisites:** preferably S1 and S3 so surviving widget tests are stable.
- **Verification:** guide-to-test reference search and existing guarded test
  command.

**Recommended first actual action:** Slice S1. It is the only required
precondition before calculator-only source retirement because the mixed ISO
table test still imports `ui.calculators_2point.py` while shared table
utilities are deliberately held.

## Task 5 - Work Plan And Lifecycle

- Added the shared utility retention decision to `docs/WORK_PLAN.md`, recording
  quarantine/hold for `ui/spreadsheet_table.py` and `ui/theme.py`, retention of
  independent utility/environment tests, the mixed-test prerequisite, and
  later support-matrix narrowing.
- `project_log.md` is not modified: this scoped decision implements the already
  recorded retirement sequence and does not change runtime architecture or
  process guardrails.
- `ACTIVE_DOCUMENTS.md` is not modified: no active document is created,
  retired, moved, or re-owned in this decision-only task.
- `result_reports/memory/project_memory_seed.md` is not modified: seed sync is
  reserved for summary lifecycle or explicit memory maintenance.
- Result report lifecycle maintenance is excluded by task scope.

## Task 6 - Verification

- `python3 -B tools/check_code_structure.py`:
  `code structure guard: OK (no findings)`.
- Retained shared/held PyQt test run:
  `python3 -B -m pytest tests/test_iso16358_table_excel_like_behavior.py tests/test_spreadsheet_table_model.py tests/test_spreadsheet_table_view.py tests/test_ui_theme_tokens.py tests/test_pyqt_environment_guard.py -q -rxXs`
  completed with `95 passed, 31 skipped in 0.17s`; skips remain attributable
  to the known-bad macOS Python 3.14 + PyQt5 widget guard.
- Full suite:
  `python3 -B -m pytest -q -rxXs` completed with
  `566 passed, 32 skipped, 19 xfailed in 1.83s`.
- The full suite matches the post-155 decision-only baseline exactly, and no
  native abort occurred.

## Changed Files

- `docs/WORK_PLAN.md` - records the retention decision and ordered prerequisite
  for later source retirement.
- `result_reports/active/156_shared-pyqt-utility-retention-decision.md` -
  records evidence, decisions, follow-up slices, and verification.

## Known Risks

- Held utilities currently have no retained non-calculator runtime importer;
  their value is preserving tested reusable capability and active SSOT
  alignment until a future PyQt consumer or decomposition decision exists.
- Until S1, the mixed ISO table test remains coupled to a calculator-only
  source candidate and blocks a clean source-retirement slice.
- The support matrix guide still mentions tests retired in 155 until its
  separately scoped narrowing update is performed.

## Scope Compliance

- No source, test, import, support matrix, architecture, Predict/Train,
  Tkinter, core/profile/dispatcher, marker, fixture, expected value, project
  log, active-document index, or memory-seed file was modified.
- No deletion, move, rename, source retirement, or report lifecycle
  maintenance was performed.

## Commit / Push

Source/test/runtime change: none; permitted `docs/WORK_PLAN.md` and this
report only.

- Decision/docs commit: `a72f7b1` (`audit: decide shared PyQt utility retention`)
- Report commit: this report is committed separately after finalization.
- Push: both commits are pushed together to `origin/work/ui-ux-ssot-adoption`
  after the report commit.

## Project Memory Delta

```yaml
- type: decision
  topic: shared-pyqt-utility-retention
  content: "After PyQt calculator direct-test retirement, ui/spreadsheet_table.py and ui/theme.py remain quarantine/hold assets because they have tested reusable PyQt/token behavior and active UI/UX contract ownership, despite currently having only calculator runtime consumers."
  keywords:
    - PyQt
    - spreadsheet_table
    - theme
    - shared utility
    - retirement
  assertionStatus: observed
  source: result_reports/active/156_shared-pyqt-utility-retention-decision.md (Task 3 - Retention Decisions)
- type: decision
  topic: pyqt-widget-guard-retention
  content: "The PyQt known-bad environment guard and support matrix guide remain required while retained guarded widget tests survive; the guide should be narrowed later rather than deleted with calculator-only source."
  keywords:
    - PyQt
    - pyqt_env
    - support matrix
    - widget tests
    - retirement
  assertionStatus: observed
  source: result_reports/active/156_shared-pyqt-utility-retention-decision.md (Task 3 - Retention Decisions)
```

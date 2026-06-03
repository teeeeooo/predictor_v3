# 154 - PyQt Calculator-Only Retirement Audit

## Goal

Audit the reference relationships and preservation boundary for retiring the
PyQt calculator-only path without retiring PyQt Predict/Train applications or
modifying runtime/test implementation.

## Scope

- Read-only inventory of PyQt calculator-related source, tests, and active
  documentation.
- Classification of retirement, retention, shared, test-only, docs-only, and
  follow-up candidates.
- A small-slice follow-up order for any future retirement work.
- A short update to `docs/WORK_PLAN.md` recording the completed audit and next
  action.

## Non-goals

- No source, import, test, fixture, marker, expected value, core calculator,
  profile, dispatcher, or architecture-document changes.
- No file deletion, move, rename, PyQt retirement execution, Tkinter feature
  implementation, packaging run, report lifecycle maintenance, or memory seed
  maintenance.
- No proposal to remove PyQt Predict/Train applications.

## Project Memory Recall Gate

The required keyword-limited search of
`result_reports/memory/project_memory_seed.md` found:

- The PyQt calculator-only packaging direction is on hold while the lightweight
  Tkinter direction is evaluated; the single-file Tkinter spike was not accepted
  as the lasting module structure.
- The new-code quality gate is project-wide and requires thin app entrypoints,
  layer import boundaries, and structure-guard verification for
  structure-impacting work.
- The macOS Python 3.14 + PyQt5 widget-test native abort is a known environment
  issue addressed by a targeted skip guard.
- PyQt Predict/Train applications are retention candidates while PyQt
  calculator-only assets are candidates for this read-only retirement audit.

These entries were used as evidence only. Current prompt constraints,
`AGENTS.md`, router requirements, and current source/doc references governed
the classification. The memory seed was not modified, and source reports did
not need to be opened beyond already active summary/reference evidence.

## Task 1 - Source Inventory

### Runtime reference chain

| Path | Direct evidence | Classification | Audit judgment |
| --- | --- | --- | --- |
| `app_calculator.py` | imports `ui.calc_window.CalculatorWindow` only for PyQt calculator launch | 1. calculator-only retirement candidate | direct calculator entrypoint candidate |
| `ui/calc_window.py` | imported by `app_calculator.py`; imports calculator tables, theme, and error helper | 1. calculator-only retirement candidate | direct calculator shell candidate |
| `ui/calculators_2point.py` | dynamically imported only from `ui/calc_window.py`; ISO calculator widgets/models | 1. calculator-only retirement candidate | direct calculator UI candidate |
| `ui/calculator_errors.py` | imported by `ui/calc_window.py`; imports `ui.theme`; tests protect extracted calculator validation helper | 1. calculator-only retirement candidate | no non-calculator runtime consumer found |
| `app_predict.py` | imports `ui.predict_window.PredictWindow` | 2. Predict/Train active dependency | retain |
| `ui/predict_window.py` | imports `ui.base_model` and `ui.base_view` | 2. Predict/Train active dependency | retain |
| `ui/base_model.py` | used by `ui.predict_window.py` | 2. Predict/Train active dependency | retain |
| `ui/base_view.py` | used by `ui.predict_window.py` | 2. Predict/Train active dependency | retain |
| `app_train.py` | imports `ui.train_window.TrainWindow` | 2. Predict/Train active dependency | retain |
| `ui/train_window.py` | used by `app_train.py`; also reaches PyQt-based mapping selection through existing training path | 2. Predict/Train active dependency | retain |
| `ui/spreadsheet_table.py` | runtime imports only from calculator modules; active table SSOT describes it as a reusable table component; dedicated model/view tests exist | 6. uncertain, needs follow-up | quarantine/hold pending shared-utility retention decision |
| `ui/theme.py` | runtime imports only from `ui/calc_window.py` and `ui/calculator_errors.py`; token tests and UI/UX design-token ownership exist | 6. uncertain, needs follow-up | quarantine/hold pending token utility retention decision |

### Calculator-only candidates

- `app_calculator.py`
- `ui/calc_window.py`
- `ui/calculators_2point.py`
- `ui/calculator_errors.py`

This is an audit classification, not an authorization to delete or modify any
file.

### Predict/Train retention candidates

- `app_predict.py`
- `app_train.py`
- `ui/predict_window.py`
- `ui/train_window.py`
- `ui/base_model.py`
- `ui/base_view.py`
- Existing PyQt support required by those entrypoints, including
  `scripts/update_mapping.py` as imported by `ui/train_window.py`.

### Shared or uncertain candidates

- `ui/spreadsheet_table.py`: no current Predict/Train runtime import was found,
  but it is represented as reusable PyQt table infrastructure by active UI/UX
  docs and has independent model/view regression tests. Do not classify it for
  deletion until its intended post-calculator owner is decided.
- `ui/theme.py`: no current Predict/Train runtime import was found, but it is a
  PyQt-independent token registry linked to active design-token ownership and
  independently tested. Do not classify it for deletion with calculator shell
  removal.

## Task 2 - PyQt Calculator-Related Test Inventory

| Test path | Protected surface | Classification | Follow-up judgment |
| --- | --- | --- | --- |
| `tests/test_app_calculator_ui_smoke.py` | `CalculatorWindow`, profile dispatch, AHRI/EN tables/results, validation error path | calculator-only source test | deletion/quarantine candidate with calculator shell retirement |
| `tests/test_iso16358_result_table_copy_tsv.py` | models/views from `ui.calculators_2point.py` | calculator-only source test | deletion/quarantine candidate with `calculators_2point` retirement |
| `tests/test_iso16358_table_excel_like_behavior.py` | `ui.calculators_2point` input grid plus shared TSV helpers | mixed calculator/shared reference | uncertain; split judgment required before removal |
| `tests/test_calculator_errors.py` | `ui.calculator_errors` and theme-token error styling | calculator-only helper test with token dependency | deletion/quarantine candidate only with helper retirement |
| `tests/test_spreadsheet_table_model.py` | reusable spreadsheet model, factories, signals | shared/uncertain utility test | keep pending shared utility retention decision |
| `tests/test_spreadsheet_table_view.py` | reusable `SpreadsheetTableView` interactions | shared/uncertain PyQt utility test | keep pending shared utility retention decision |
| `tests/test_ui_theme_tokens.py` | token registry; explicitly importable without PyQt5 | shared/uncertain utility test | keep pending theme retention decision |
| `tests/helpers/pyqt_env.py` | known-bad PyQt widget host detection and skip helpers | 4. test-only utility | keep while any guarded PyQt widget test remains |
| `tests/test_pyqt_environment_guard.py` | environment guard policy correctness | 4. test-only utility | keep with the helper/support policy |

The four guarded widget tests are `tests/test_app_calculator_ui_smoke.py`,
`tests/test_iso16358_result_table_copy_tsv.py`,
`tests/test_iso16358_table_excel_like_behavior.py`, and
`tests/test_spreadsheet_table_view.py`. Retirement of calculator-direct tests
does not by itself retire `tests/helpers/pyqt_env.py`, because the shared
spreadsheet view test remains a guarded PyQt widget surface until separately
decided.

## Task 3 - Documentation References

### Active docs update candidates after actual retirement

| Document | Reference found | Future handling candidate |
| --- | --- | --- |
| `README.md` | lists `ui/`, `app_calculator.py` as calculator UI entrypoints | update after entrypoint retirement |
| `project_brief.md` | describes `app_calculator.py` / `ui/calc_window.py` as current protected PyQt calculator path | update after actual retirement, not during audit |
| `docs/WORK_PLAN.md` | contains current hold state and audit as next action | updated in this audit to record result and slices |
| `docs/architecture/project_architecture.md` | owns `calc_window.py` routing/module-boundary text | update only in later source retirement/docs slice; prohibited here |
| `docs/designs/2026-05-22-calculator-ui-module-boundary.md` | plans continued calculator module extractions | mark superseded/held only in a dedicated docs decision slice if retirement proceeds |
| `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md` | retains PyQt calculator stack as fallback/reference and packaging baseline | retain as decision record; evaluate small status update only after retirement decision |
| `docs/guides/lightweight_calculator_packaging_check.md` | uses `app_calculator.py` as the PyQt size baseline | keep or revise depending on whether comparative packaging baseline is still required |
| `docs/guides/pyqt_test_support_matrix.md` | inventories calculator widget tests and PyQt environment skip policy | retain now; after test retirement, narrow it to surviving PyQt widget/support tests or retire it only if no supported surface remains |
| `ACTIVE_DOCUMENTS.md` | registers support matrix and active UI/UX owner docs | no audit edit; revisit only if a registered document is retired or scope changes |

### Docs to retain independent of calculator-only retirement

- `docs/ui_ux/00_UI_UX_SYSTEM.md`,
  `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`,
  `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`,
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`, and
  `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md` are active UI/UX
  governance for possible PyQt surfaces, including retained Predict/Train or
  future table work; they are not calculator-only deletion candidates.

### Historical references

- `result_reports/summaries/081_*`, `101_*`, `114_*`, `123_*`, and `132_*`
  preserve historical decisions and audit provenance. They are not rewrite
  targets for future source retirement.
- `project_log.md` already records the PyQt/Tkinter stabilization direction and
  the retirement audit as the next read-only action. Per the task instruction,
  it is not modified for this audit.

## Task 4 - Proposed Retirement Slices

### Slice R1 - PyQt Calculator-Only Test Retirement

- **Purpose:** remove or quarantine tests whose only production owner is the
  PyQt calculator-only shell/modules after confirming retirement is approved.
- **Target files:** `tests/test_app_calculator_ui_smoke.py`,
  `tests/test_iso16358_result_table_copy_tsv.py`,
  `tests/test_calculator_errors.py`; assess
  `tests/test_iso16358_table_excel_like_behavior.py` separately because it
  includes shared helper coverage.
- **Included scope:** direct calculator-only tests and resulting test inventory
  update.
- **Excluded scope:** source deletion, shared model/view/theme tests, PyQt
  environment helper deletion, marker/fixture alteration unrelated to deleted
  tests.
- **Prerequisites:** explicit retirement authorization and final
  `ui/spreadsheet_table.py` ownership judgment for the mixed ISO table test.
- **Verification:** focused test collection check plus full
  `python3 -B -m pytest -q -rxXs`; explain expected count delta.

### Slice R2 - Shared PyQt Utility Retention Decision

- **Purpose:** decide whether `ui/spreadsheet_table.py` and `ui/theme.py`
  remain as shared/held infrastructure or may follow calculator retirement.
- **Target files:** `ui/spreadsheet_table.py`, `ui/theme.py`,
  `tests/test_spreadsheet_table_model.py`, `tests/test_spreadsheet_table_view.py`,
  `tests/test_ui_theme_tokens.py`, active UI/UX owner docs.
- **Included scope:** reference/owner decision and any specifically authorized
  status documentation.
- **Excluded scope:** Predict/Train removal and calculator source deletion.
- **Prerequisites:** agreement on whether retained/future PyQt table surfaces
  consume these utilities.
- **Verification:** reference inventory; focused surviving tests if files are
  retained or changed.

### Slice R3 - PyQt Calculator-Only Source Retirement

- **Purpose:** remove calculator-only PyQt runtime surface after test and shared
  ownership decisions are resolved.
- **Target files:** `app_calculator.py`, `ui/calc_window.py`,
  `ui/calculators_2point.py`, `ui/calculator_errors.py`; include shared files
  only if R2 separately authorizes it.
- **Included scope:** approved source removal and strictly necessary import or
  packaging-entry cleanup.
- **Excluded scope:** `app_predict.py`, `app_train.py`, Predict/Train UI,
  shared utilities without R2 disposition, Tkinter additions, core/profile
  changes.
- **Prerequisites:** R1 and R2 decisions completed; docs update candidates
  enumerated.
- **Verification:** `python3 -B tools/check_code_structure.py`, import smoke for
  retained entrypoints, full pytest suite.

### Slice R4 - PyQt Calculator-Only Active Docs Update

- **Purpose:** align active user-facing and architecture/status documentation
  after actual source retirement.
- **Target files:** `README.md`, `project_brief.md`, `docs/WORK_PLAN.md`,
  applicable sections of `docs/architecture/project_architecture.md` and
  calculator design records.
- **Included scope:** current-state wording and removed entrypoint references.
- **Excluded scope:** historical report/archive rewrites and unrelated UI/UX
  contract changes.
- **Prerequisites:** R3 completed or an explicit final retirement decision.
- **Verification:** targeted `rg` for retired path references, with retained
  historical/reference matches documented.

### Slice R5 - PyQt Support Matrix Guide Update Or Retirement

- **Purpose:** match the PyQt environment policy guide to remaining guarded
  widget tests after retirement decisions.
- **Target files:** `docs/guides/pyqt_test_support_matrix.md`,
  `ACTIVE_DOCUMENTS.md` only if guide ownership/status changes, and the
  surviving PyQt environment test inventory.
- **Included scope:** preserve/narrow/retire judgment for the guide and
  registered status.
- **Excluded scope:** changing skip behavior without a separate environment
  finding.
- **Prerequisites:** R1 and R2 outcome; identify any retained PyQt widget tests.
- **Verification:** guide-to-test-reference check and existing environment guard
  tests if still retained.

**Recommended first actual retirement action:** Slice R1, limited initially to
direct calculator-only tests. It reduces obsolete protection surface before
source removal while leaving shared utility and known-bad environment policy
intact until R2 provides a defensible owner decision.

**Quarantine/hold instead of deletion:** `ui/spreadsheet_table.py`,
`ui/theme.py`, their independent tests, `tests/helpers/pyqt_env.py`,
`tests/test_pyqt_environment_guard.py`, and
`docs/guides/pyqt_test_support_matrix.md`.

## Task 5 - Work Plan And Report

- Added a concise completed-audit item to `docs/WORK_PLAN.md` identifying the
  calculator-only runtime candidates, explicit Predict/Train retention set,
  held shared-utility decision, and separated next slices.
- Created this result report.
- `project_log.md` is not updated: the active log already records the direction
  to perform this read-only audit, and this audit introduces no runtime,
  architecture, guard-test policy, or final deletion decision.
- `ACTIVE_DOCUMENTS.md` is not updated: no registered active document was
  created, retired, moved, or re-owned.
- Result report lifecycle maintenance is excluded by explicit scope; no
  active/archive/summaries movement is performed.

## Task 6 - Verification

- `python3 -B tools/check_code_structure.py`:
  `code structure guard: OK (no findings)`.
- `python3 -B -m pytest -q -rxXs`:
  `585 passed, 59 skipped, 19 xfailed in 2.75s`.
- The full suite matches the stated recent baseline exactly; this audit-only
  documentation/report change introduced no observed baseline delta.
- Pre-commit status/diff confirmation found only the permitted
  `docs/WORK_PLAN.md` modification and this new report.

## Changed Files

- `docs/WORK_PLAN.md` - records completed audit outcome and next separated
  retirement slices.
- `result_reports/active/154_pyqt-calculator-retirement-audit.md` - records
  read-only inventory, classifications, and recommended sequence.

## Known Failures / Risks

- `ui/spreadsheet_table.py` and `ui/theme.py` have no current non-calculator
  runtime importer found in this audit, but active documentation and independent
  tests present them as reusable assets; deleting them without R2 would overstate
  the evidence.
- PyQt environment guard retention depends on the surviving PyQt widget test
  set; it must not be removed merely because calculator-direct tests retire.
- This audit does not approve removal. Every retirement slice still requires an
  explicit implementation task and its own verification/baseline accounting.

## Scope Compliance

- Source, import, test, marker, fixture, expected, core, profile, dispatcher,
  PyQt runtime, Tkinter runtime, `project_log.md`, `ACTIVE_DOCUMENTS.md`, and
  `result_reports/memory/project_memory_seed.md` were not modified.
- No files were deleted, moved, renamed, archived, or lifecycle-maintained.

## Commit / Push

Source/code/test change: none. Permitted documentation/report changes only.

- Documentation commit: `83fa7f8` (`docs: record PyQt calculator retirement audit outcome`)
- Report commit: this report is committed separately after its content is
  finalized.
- Push: both commits are pushed together after the report commit.

## Project Memory Delta

```yaml
- type: fact
  topic: pyqt-calculator-retirement-boundary
  content: "Current runtime imports separate app_calculator.py, ui/calc_window.py, ui/calculators_2point.py, and ui/calculator_errors.py as PyQt calculator-only retirement candidates, while PyQt Predict/Train entrypoints and their direct UI dependencies remain retention candidates."
  keywords:
    - PyQt calculator
    - calculator-only
    - retirement
    - Predict/Train
  assertionStatus: observed
  source: result_reports/active/154_pyqt-calculator-retirement-audit.md (Task 1 - Source Inventory)
- type: open_question
  topic: pyqt-shared-utility-retention
  content: "ui/spreadsheet_table.py and ui/theme.py currently have calculator-path runtime consumers, while active UI/UX ownership and dedicated tests present them as reusable utilities; their post-calculator retention requires a separate decision before source retirement."
  keywords:
    - PyQt
    - spreadsheet_table
    - theme
    - retention
  assertionStatus: observed
  source: result_reports/active/154_pyqt-calculator-retirement-audit.md (Shared or uncertain candidates)
```

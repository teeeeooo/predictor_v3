# 217 — Table UX Target and Example Evidence Update

## Goal

Record the table UX target after the 216 Windows smoke gaps without changing
code. Keep `03_SPREADSHEET_TABLE_UX_CONTRACT.md` as the toolkit-neutral source
of truth, position SPOT as concrete example/evidence only, and move the next
implementation direction toward a common Tk table foundation preflight.

## Modified Files

- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `docs/WORK_PLAN.md`
- `project_log.md`
- `result_reports/active/217_table-ux-target-and-example-evidence-update.md`

## 03 Contract Update

- Reaffirmed that the spreadsheet table contract is the completion source of
  truth across toolkits.
- Added that concrete implementations and external examples may be used as
  behavior evidence, but do not replace the toolkit-neutral contract or become
  owner docs.
- Kept implementation details and toolkit-specific module/class names out of
  the common contract.

## Tkinter Adapter Update

- Added SPOT `InitialValuesTable` as a concrete Tkinter implementation example
  for desired table interaction behavior: paste, undo, navigation, and
  replace-on-type feel.
- Explicitly limited SPOT to example/evidence/inspiration. It is not a source
  of truth, owner doc, dependency, vendor target, or copy target.
- Recorded that `predictor_v3` should build its own common Tk table foundation
  and avoid new independent Entry/Label-grid controllers per feature.

## WORK_PLAN Update

- Replaced the immediate "Windows smoke closeout" next action with:
  `common Tk table foundation preflight`.
- Preserved the batch/detail/profile expansion arc but moved it behind the
  common table foundation path.

## project_log Entry

Added a short milestone decision:

- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` remains the source of truth.
- SPOT is concrete example/evidence, not source/dependency/copy target.
- A common Tk table foundation is needed before more independent controllers.

## SPOT Check

Checked SPOT through the GitHub Connector only. No local clone was used.

Files checked:

- `README.md`
- `ui/initial_values_table.py`
- `ui/main_screen.py`

Use scope:

- README confirmed an "initial values table" workflow with Excel paste, undo,
  Enter, and Tab style editing.
- `ui/initial_values_table.py` confirmed the table behavior is implemented as
  a concrete Tkinter interaction layer with pure helper functions for
  clipboard, navigation, key classification, and undo-related behavior.
- `ui/main_screen.py` confirmed `InitialValuesTable` is part of a real main UI
  table surface rather than a standalone demo.

SPOT code was not copied, imported, vendored, or treated as the
`predictor_v3` reference implementation.

## Not Modified

- No `ui_tk/` code was changed.
- No tests were changed or added.
- No `docs/designs` records were modified.
- No router or ACTIVE_DOCUMENTS change was needed.

## Next Action

Common Tk table foundation preflight.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft
  limit.
- `git status --short` — reviewed before commit.

Not run:

- `pytest` — docs/log/report-only change; no code or tests changed.
- GUI smoke — no UI code changed.

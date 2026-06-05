# 214A — Toolkit-neutral Table Parity Gate Update

## Goal

Strengthen the table-shaped UI completion gate so any toolkit implementation
must satisfy the toolkit-neutral Excel-like table contract, not merely render
something that looks like a table.

## Scope

- Updated the toolkit-neutral table contract.
- Clarified validation/error policy ownership.
- Clarified the Tkinter adapter as an implementation guide, not a rule source.
- Updated router gates for future table-shaped UI tasks.
- No code, test, or BatchCaseTable implementation changes.

## Changed Files

- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `AGENT_TASK_ROUTER.md`

## Contract Updates

`03_SPREADSHEET_TABLE_UX_CONTRACT.md` is now explicitly the table UX
completion source of truth across toolkits. Toolkit adapters describe
implementation methods only.

The new completion gate requires result reports to record pass/fail evidence
for the table parity checklist before a new table-shaped UI is considered
complete. If an existing reference implementation is not reused, the report
must state why and include a controller/helper-level parity test plan.

The toolkit-neutral checklist now includes:

- multi-cell rectangular selection
- copy and paste as TSV
- single-column multi-row paste
- Delete/Backspace clear
- grouped undo
- Tab/Enter and arrow-key navigation
- click/type replace-on-type
- read-only result copy and mutation prevention
- row identity as row header by default
- layout sizing acceptance

## Validation Policy Split

`05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` now points table interaction
validation back to `03` and keeps only surface-specific validation/error
policy:

- calculator auto-calc batch can keep blank, partial, or invalid rows
  result-blank while valid rows calculate independently;
- ML predict/train batch must not fail silently and needs validation summary
  and/or visible row/cell status.

## Adapter Gate

`TKINTER_TABLE_ADAPTER.md` now states that:

- it is not the rule source;
- `MetricInputTable + ExcelLikeTableController` should be reused when the
  shape fits;
- new Tk adapters/controllers need reuse rationale and controller-level
  parity tests;
- standalone `Entry`/`Label` grids are not compliant table UX;
- Windows/manual smoke is final platform verification, not the first guard
  for core interaction behavior.

## Router Gate

`AGENT_TASK_ROUTER.md` now routes table-shaped UI work through:

- `03_SPREADSHEET_TABLE_UX_CONTRACT.md`;
- the relevant toolkit adapter, or direct `03` acceptance if no adapter exists;
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` for validation/error policy.

It also requires table parity pass/fail reporting and validation-gap recording
when Windows/manual smoke first finds a core interaction bug.

## Not Changed

- No code changes.
- No tests changed.
- No current BatchCaseTable bug fixes.
- No docs/designs changes.
- No project_log update; the detailed process decision is captured in this
  active report and the existing project log already records the broader UI
  contract guardrail arc.

## Verification

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the pre-existing
  `ui_tk/sections/bin_detail_panel.py` LOC soft warning.
- `git status --short` — only the intended docs/report files were modified.

Not run:

- `pytest` — not run because this is a docs/router gate update with no code
  or test changes.
- GUI smoke — not run because no UI implementation changed.

## Next Action

214B should fix the current batch table smoke issues against this parity gate:
grouped undo, row-header identity instead of `Case` input column,
single-column multi-row paste, arrow navigation, and main-screen lower-space
sizing.

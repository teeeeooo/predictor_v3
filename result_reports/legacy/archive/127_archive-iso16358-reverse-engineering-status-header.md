# 127 Archive ISO16358 Reverse Engineering Status Header

## Goal

Clarify that `docs/archive/iso16358_initial_reverse_engineering/` is a historical initial reverse-engineering snapshot, not a current runtime/import/test/calculator source.

## Scope

- `docs/archive/iso16358_initial_reverse_engineering/`
- `docs/archive/iso16358_initial_reverse_engineering/README.md`
- `docs/WORK_PLAN.md`
- `result_reports/archive/121_legacy-unused-script-cleanup-audit.md`

## Non-Goals

- Delete files.
- Move files.
- Rename files.
- Modify archive script bodies.
- Change imports.
- Modify tests, expected values, fixtures, core calculator code, profile/dispatcher code, PyQt/Tkinter code, or AS/NZS compatibility behavior.
- Perform result report lifecycle maintenance.

## Task 1 Result

Archive folder file list:

- `docs/archive/iso16358_initial_reverse_engineering/README.md`
- `docs/archive/iso16358_initial_reverse_engineering/cspf_calculator.py`
- `docs/archive/iso16358_initial_reverse_engineering/dump_bin_inputs.py`
- `docs/archive/iso16358_initial_reverse_engineering/dump_bins.py`
- `docs/archive/iso16358_initial_reverse_engineering/extract_formulas.py`
- `docs/archive/iso16358_initial_reverse_engineering/find_cspf.py`
- `docs/archive/iso16358_initial_reverse_engineering/formula_list.txt`

Tracked file check:

- `git ls-files docs/archive/iso16358_initial_reverse_engineering` lists only the README, five `.py` files, and `formula_list.txt`.
- `docs/archive/iso16358_initial_reverse_engineering/__pycache__/` exists locally and is ignored (`git status --short --ignored ...` reports `!! .../__pycache__/`).
- The ignored `__pycache__` artifact was not deleted, moved, or modified.

Runtime/import reference check:

- `rg "iso16358_initial_reverse_engineering|cspf_calculator|dump_bin_inputs|dump_bins|extract_formulas|find_cspf" . -n` was executed.
- No current production runtime/import/test/calculator path imports these archive scripts.
- Hits inside `docs/archive/iso16358_initial_reverse_engineering/*.py` are script-internal function names or direct script entrypoint calls.
- Historical/reference mentions remain in:
  - `project_log.md`
  - `docs/iso16358/iso16358_dev_notes.md`
  - `result_reports/archive/121_legacy-unused-script-cleanup-audit.md`
  - `docs/WORK_PLAN.md`

README status before this task:

- The README already said the folder is for early one-off ISO16358-1 AMD1 reverse-engineering scripts and formula extraction results.
- It also said the files are not the current production calculation path.
- It did not yet have a compact status header explicitly covering runtime/import/test/calculator separation, deletion/move/rename policy, and where to find current ISO16358 status.

## Task 2 Result

Updated `docs/archive/iso16358_initial_reverse_engineering/README.md` with a short `## Status` header.

The header now states:

- The folder is a historical archive / initial reverse-engineering snapshot.
- It is not imported by current production runtime, tests, or calculator paths.
- The files preserve historical analysis context and are not active calculator implementation source.
- Delete / move / rename requires a separate archive cleanup decision.
- Current ISO16358 calculator status should be read from active docs, `docs/WORK_PLAN.md`, and relevant tests.

The existing historical context below the header was preserved.

## Task 3 Result

Updated `docs/WORK_PLAN.md` narrowly:

- Marked legacy cleanup Slice C2 as complete.
- Recorded that `docs/archive/iso16358_initial_reverse_engineering/` is a historical archive / initial reverse-engineering snapshot and not runtime/import/test/calculator path input.
- Recorded that no delete / move / rename was performed.
- Kept AS/NZS exact reconstruction as deferred Z-phase work.
- Kept remaining xfail status unchanged at 19.

Next recommended actions:

1. Windows PyInstaller size measurement when a Windows host is available.
2. PyQt fatal-abort environment handling.
3. Tkinter ISO section pure helper cleanup, if needed.
4. Legacy cleanup follow-up audit, if needed.

Lifecycle maintenance was not performed because this task only created a single active report and did not summarize/archive active reports.

## Task 4 Result

Verification:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `rg "iso16358_initial_reverse_engineering|cspf_calculator|dump_bin_inputs|dump_bins|extract_formulas|find_cspf" . -n` -> historical docs/report mentions plus archive script self-references only; no active runtime/import path found.
- `python3 -B -m pytest tests/test_code_structure_guard.py -q` -> `20 passed`.

No files were deleted, moved, or renamed.

## Changed Files

- `docs/archive/iso16358_initial_reverse_engineering/README.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/127_archive-iso16358-reverse-engineering-status-header.md`

## Residual Risk

- The ignored local `__pycache__/` remains in the working tree as a runtime artifact, but it is not tracked and was intentionally left untouched.
- Historical references in older docs/reports still mention these scripts as archive material; those records were intentionally not rewritten.

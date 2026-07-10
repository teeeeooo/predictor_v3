# KOREA Sub-Arc Closeout

## Goal

Close out Calculator Sub-Arc - KOREA Notebook Entry and return the near-term
execution board to Arc 13.5.

## Scope

- Updated `docs/WORK_PLAN.md` so Arc 13.5 Slice 0 is the next action.
- Updated `project_brief.md` KOREA sub-arc status to complete.
- Appended a milestone-level `project_log.md` entry for the KOREA closeout.
- Ran the closeout validation set for KOREA calculator UI/application/batch
  paths and related profile/dispatcher guards.

## Completion Check

- KOREA top-level tab: implemented.
- CSPF/HSPF single calculation UI: implemented.
- CSPF/HSPF midpoint guide tables: implemented.
- CSPF/HSPF batch table dialogs: implemented.
- CSPF/HSPF detail views: implemented.
- KS C 9306 core formula/config/profile/public result contracts: preserved.

## Verification

- `python3 -B -m compileall -q apps/calculator core/calculators tests`: OK.
- `python3 -B -m pytest -q tests/test_calculator_korea_cspf_usecase.py tests/test_calculator_korea_hspf_usecase.py tests/test_calculator_korea_detail_contract.py tests/test_ui_tk_korea_batch_profiles.py tests/test_apps_calculator_ui_korea_tab.py`:
  OK with headless Tk skips, 16 passed and 2 skipped.
- `python3 -B -m pytest -q tests/test_calculator_dispatcher.py tests/test_calculator_profiles.py`:
  OK, 40 passed.
- `python3 -B tools/check_code_structure.py`: OK with 9 pre-existing soft
  warnings outside the closeout docs.
- `git diff --check`: OK.
- `git status --short`: reviewed before closeout commit.

## Known Risks

- Tk manual smoke could not be run in this headless environment. Manual smoke
  remains useful for visible notebook switching, dialog open/preserve behavior,
  detail toggle/refit, and scroll/viewport behavior.
- Active report count is now above the lightweight threshold; report lifecycle
  summary/archive cleanup should be a follow-up after this pushed closeout.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: performed after Slice 6 closeout commit; remote match is reported in
  the terminal response.

# 384 EN14825 Table Input Consistency Correction

## Goal

Remove the EN14825 form-entry undo rollback helper and align EN14825 numeric
auxiliary inputs with the existing `MetricInputTable` + `TkTableController`
interaction path.

## Scope

- Replaced EN14825 common numeric Pto/Psb/Pck/Poff form entries with
  `MetricInputTable` surfaces and `TkTableController` instances.
- Replaced SEER Pdesignc/Tdesignc/Cd form entries with a design
  `MetricInputTable` and controller.
- Replaced SCOP Cd and per-climate Pdesignh/Tbiv/TOL form entries with
  `MetricInputTable` surfaces and controllers.
- Kept the appliance type as a readonly dropdown because it is not a numeric
  table input.
- Kept existing StringVar-backed provider/wiring so calculation callers still
  read the same auxiliary values.
- Deleted `apps/calculator/ui/form_entry_undo.py`.

## Non-goals

- No core, data, fixture, golden, adapter model, or calculation logic changes.
- No `MetricInputTable` / `TkTableController` refactor.
- No new form undo/helper/controller.
- No appliance type table conversion.

## Reference Parity

- Existing reference checked: `MetricInputTable` surface adapter methods and
  `TkTableController` selection/copy/paste/clear/undo/navigation implementation.
- Reuse decision: numeric auxiliary inputs now use that existing tested path
  instead of a one-off form Entry undo helper.
- Parity checklist status: rectangular selection, TSV copy/paste, clear,
  grouped undo, navigation, replace-on-type, and readonly mutation prevention
  are inherited from `TkTableController` for the new auxiliary tables.
- Remaining manual parity gap: target desktop smoke should still verify visible
  EN14825 auxiliary table selection/copy/paste/Ctrl/Cmd-Z behavior.

## Verification

- `python3 -B -m py_compile apps/calculator/ui/tabs/en14825_tab.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_seer_section.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q` OK, 18 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 24 passed.
- `python3 -B -m pytest tests/test_ui_tk_calculator_foundation.py -q` OK, 24 passed.
- `python3 -B tools/check_code_structure.py` OK with one soft LOC warning.
- `git diff --check` OK.
- `git status --short` OK before report creation and showed only report work afterward.

## Structure Warnings

- `apps/calculator/ui/sections/en14825_scop_section.py` exceeds the 400 LOC
  soft limit after this slice.

## Warning Triage

- Current responsibilities: SCOP section composition, climate card assembly,
  auxiliary input synchronization, table calculation refresh, and result
  surface updates.
- Still belongs here for this slice: small StringVar/table synchronization
  needed to preserve existing calculation provider behavior while switching
  widgets to the tested table controller path.
- Candidate split: climate card auxiliary input subcomponent if the next SCOP
  work adds more card-level layout or lifecycle responsibility.
- Action: accepted for this slice with reason; split audit required before the
  next SCOP code slice that adds responsibility to this file.

## Task Results

- Removed the duplicate form-entry undo implementation.
- Common EN14825 numeric inputs now use table controller undo/copy/paste path
  while preserving shared SEER/SCOP common value synchronization.
- SEER design and SCOP design/condition numeric inputs now use table controller
  undo path and remain synchronized with existing calculation variables.
- Focused tests now assert table-controller undo synchronization instead of
  form-entry helper behavior.
- `docs/WORK_PLAN.md` updated to record the rollback and revised smoke target.

## Changed Files

- `apps/calculator/ui/tabs/en14825_tab.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- `apps/calculator/ui/form_entry_undo.py` deleted
- `tests/test_apps_calculator_ui_en14825.py`
- `tests/test_apps_calculator_ui_en14825_scop.py`
- `docs/WORK_PLAN.md`

## Known Failures / Risks

- No automated OS-level keyboard smoke was run for visible windows.
- SCOP section remains above the soft LOC threshold; further SCOP UI
  responsibility should start with a split audit.
- Active report count exceeds lifecycle threshold; cleanup remains a separate
  follow-up.

## Next Suggested Action

- Manual smoke EN14825 auxiliary tables on the target desktop for selection,
  copy/paste, clear, and Ctrl/Cmd-Z.
- Defer SCOP climate card extraction unless follow-up UI work adds more
  responsibility to the same section.

## Scope Compliance

- Calculation logic, core/data files, fixtures, goldens, public schemas, and
  table controller internals were not changed.
- Appliance type remains a dropdown without the removed undo helper.

## Commit / Push

- Source/docs/tests commit: `6662395` (`Align EN14825 auxiliary inputs with table controller`).
- Report commit hash and push result are reported in terminal output to avoid a
  self-referential report update loop.

## Project Memory Delta

- none

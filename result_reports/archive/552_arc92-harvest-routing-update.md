# Arc 9.2 Harvest Routing Update

## Goal

Route the moved PySide6 visual/table parity harvest through project-specific
design references while keeping `docs/ui_ux/` as a portable UI/UX contract set.

## Changed Files

- `docs/ui_ux/README.md`
- `docs/designs/README.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`

## Routing Updates

- Removed the project-specific harvest from the portable `docs/ui_ux/` document
  list.
- Added `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md` to the
  design index as the Arc 9.5 design/acceptance reference.
- Updated the PySide6 architecture contract to route visual/table harvest
  evidence through the new design path.
- Updated Work Plan and Project Brief phase wording to place Arc 9.2 between
  legacy UI retirement and Arc 9.5 visual parity implementation.

## Excluded Scope

- No production code changes.
- No `apps/`, `core/`, `scripts/`, `tests/`, or `ui_common/` changes.
- No legacy `ui/` restoration.
- No PySide6 visual parity implementation.

## Verification

- Stale path search: old `docs/ui_ux/06_PYSIDE6_VISUAL_AND_TABLE_PARITY_HARVEST.md`
  path no longer appears in active docs searched outside archive.
- `git diff --check`: to be run before slice closeout.
- `git status --short`: to be run before slice closeout.

## Next Action

Run Arc 9.2 closeout validation, write closeout report, then proceed to Arc 9.5
Predict / Train Visual UI Parity from Design Assets.

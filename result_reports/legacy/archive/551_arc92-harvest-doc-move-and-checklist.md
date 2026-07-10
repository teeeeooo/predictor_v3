# Arc 9.2 Harvest Doc Move And Checklist

## Goal

Move the PySide6 visual/table parity harvest out of the portable `docs/ui_ux/`
rule set and expand it into an Arc 9.5 design acceptance reference.

## Scope

- Moved harvest document to:
  `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`
- Reframed it as a project-specific design/harvest reference.
- Added detailed Arc 9.5 acceptance checklist sections.

## Changed Content

- Predict table visual/interaction parity.
- Spreadsheet interaction parity.
- Mapping/autofill parity.
- Row-to-ML/result parity.
- Predict surface visual hierarchy.
- Train admin visual/function inventory.
- Visual token adoption.
- Deferred items split by Arc 9.5, Arc 10, Arc 11, and later.

## Excluded Scope

- No production code changes.
- No legacy `ui/` restoration.
- No PySide6 implementation.
- No worker/progress/cancel implementation.
- No trainer execution implementation.

## Verification

- `git diff --check`: to be run before slice closeout.
- `git status --short`: to be run before slice closeout.

## Next Action

Update routing documents so the moved design harvest is discoverable for Arc
9.5 while `docs/ui_ux/` remains portable contract ownership.

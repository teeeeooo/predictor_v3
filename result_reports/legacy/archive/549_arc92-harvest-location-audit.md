# Arc 9.2 Harvest Location Audit

## Goal

Confirm whether the current PySide6 visual/table parity harvest belongs under
the portable `docs/ui_ux/` rule set or under project-specific design records.

## Scope

- Checked `docs/ui_ux/README.md` role wording.
- Checked current `docs/ui_ux/06_PYSIDE6_VISUAL_AND_TABLE_PARITY_HARVEST.md`.
- Checked current routing references in `ACTIVE_DOCUMENTS.md`,
  `docs/designs/README.md`, `docs/WORK_PLAN.md`, `project_brief.md`, and
  `docs/architecture/pyside6_train_predict_architecture.md`.

## Decision

The harvest document should move to:

- `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`

Reason:

- `docs/ui_ux/README.md` defines `docs/ui_ux/` as a portable UI/UX rule set.
- The harvest document is predictor_v3-specific legacy evidence for the
  PySide6 Train/Predict rewrite.
- The document is tied to design assets and Arc 9.5 implementation acceptance,
  not to portable toolkit-neutral rule ownership.

## Follow-up References To Update

- `docs/ui_ux/README.md`
- `docs/designs/README.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `docs/architecture/pyside6_train_predict_architecture.md`

## Excluded Scope

- No production code changes.
- No `ui/` restoration.
- No PySide6 visual parity implementation.
- No dependency or model/schema/calculator changes.

## Verification

- `git status --short`: checked before report creation.
- `git diff --check`: to be run before slice closeout.

## Next Action

Recover detailed legacy UI behavior from Git history before expanding the moved
design harvest document.

# 545 Arc 9.1 Legacy UX Harvest

## Goal

Preserve useful legacy Train/Predict UX ideas as documentation before deleting
the legacy `ui/` folder.

## Changes

- Added `docs/ui_ux/06_PYSIDE6_VISUAL_AND_TABLE_PARITY_HARVEST.md`.
- Updated `docs/ui_ux/README.md` so the harvest document is discoverable.
- Updated `docs/designs/README.md` so the PySide6 design gate points to the
  harvest doc and treats visual assets as Arc 9.5 layout references, not
  pixel-perfect targets.

## Harvested Ideas

- `ui/base_view.py`: dropdown affordance, one-click popup, non-editing dropdown
  arrow rendering.
- `ui/spreadsheet_table.py`: TSV copy/paste, selection clear, undo, numeric
  invalid-state ideas.
- `ui/theme.py`: semantic token idea, consolidated under
  `ui_common.visual_tokens`.
- `ui/predict_window.py` and `ui/train_window.py`: feature inventory only.

## Boundary Decision

- Legacy code is not copied into PySide6.
- The harvest document is reference/evidence, not a new owner contract.
- Active table behavior remains owned by
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Active visual token foundation remains `ui_common.visual_tokens`.

## Verification

- `git diff --check`: pending for slice closeout.
- `git status --short`: pending for slice closeout.

## Excluded Scope

- No Arc 9.5 visual implementation.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.
- No ML, mapping schema, calculator, fixture, golden, or model artifact changes.

## Next Action

Arc 9.1 Slice 3 - adopt `ui_common.visual_tokens` as the active visual token
owner.

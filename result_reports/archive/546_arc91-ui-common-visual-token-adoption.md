# 546 Arc 9.1 ui_common Visual Token Adoption

## Goal

Adopt `ui_common.visual_tokens` as the active toolkit-neutral visual token owner
for Arc 9.5 Predict/Train visual parity work.

## Changes

- Expanded `ui_common/visual_tokens.py` with semantic roles harvested from
  legacy token ideas:
  - `surface.header`
  - `text.disabled`
  - `action.primary`
  - panel/cell/row/outer spacing aliases
  - window, panel, and table font roles.
- Updated `tests/test_visual_tokens.py` to cover the expanded role contract.
- Updated `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` to identify
  `ui_common.visual_tokens` as the active predictor_v3 token owner for Arc 9.5.

## Boundary Decision

- `ui_common.visual_tokens` remains toolkit-neutral.
- No PyQt5, PySide6, or tkinter imports were added.
- No PySide6 style adapter or visual parity implementation was started.
- Legacy `ui/theme.py` remains a deletion target for Slice 4; its reusable
  token ideas are now covered by `ui_common.visual_tokens` and the harvest doc.

## Verification

- `python3 -B -m py_compile ui_common/*.py`
- `python3 -B -c "from ui_common.visual_tokens import visual_color, visual_spacing, visual_font; assert visual_color('surface.default'); assert visual_spacing('space.sm') > 0; assert visual_font('font.body')"`
- `python3 -B -m pytest tests/test_visual_tokens.py`
- `rg -n "PyQt5|PySide6|tkinter" ui_common || true`
- `git diff --check`
- `git status --short`

## Excluded Scope

- No Arc 9.5 visual implementation.
- No PySide6 adapter implementation.
- No worker/progress/cancel implementation.
- No ML, mapping schema, calculator, fixture, golden, or model artifact changes.

## Next Action

Arc 9.1 Slice 4 - retire the legacy PyQt `ui/` folder and legacy tests.

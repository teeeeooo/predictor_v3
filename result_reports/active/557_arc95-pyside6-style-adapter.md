# 557 - Arc 9.5 PySide6 Style Adapter

## Goal

Create a shared PySide6 style adapter so Predict and Train visual parity slices
can apply `ui_common.visual_tokens` without scattering raw colors, spacing,
radius, or font values across widgets.

## Changes

- Added `apps/common/ui/style.py`.
- Added shared package markers:
  - `apps/common/__init__.py`
  - `apps/common/ui/__init__.py`
- Added minimal Arc 9.5 token roles to `ui_common.visual_tokens`:
  - `accent.primary`
  - `table.result`
  - `status.neutral`
  - `status.ready`
  - `status.missing`
  - `status.running`
- Added focused adapter tests in `tests/test_pyside6_style_adapter.py`.
- Updated `tests/test_visual_tokens.py` expected roles.

## Boundary Decision

`apps/common/ui/style.py` is an app-layer PySide6 adapter. It may import
PySide6 and convert toolkit-neutral roles into `QColor`, `QFont`, and
stylesheet snippets. `ui_common.visual_tokens` remains toolkit-neutral and
imports no GUI toolkit.

This shared adapter avoids duplicating style conversion in both
`apps/predict/ui/` and `apps/train/ui/`.

## Excluded Scope

- Did not apply the adapter broadly to screens yet; that is Slice 3 / Slice 6.
- Did not implement worker/progress/cancel.
- Did not implement Trainer execution or mapping Excel update execution.
- Did not change ML behavior, mapping schema, model artifact, calculator logic,
  fixtures, golden values, or public result contracts.

## Verification

- `python3 -B -m py_compile ui_common/*.py apps/predict/**/*.py apps/train/**/*.py apps/common/**/*.py`: passed.
- `python3 -B -c "from ui_common.visual_tokens import visual_color, visual_spacing, visual_font; assert visual_color('surface.default'); assert visual_spacing('space.sm') > 0; assert visual_font('font.body')"`: passed.
- `python3 -B -c "import app_predict; import app_train"`: passed.
- `rg -n "PyQt5|from ui\\.|import ui\\." apps core tests scripts docs ui_common --glob "!result_reports/archive/**" --glob "!docs/archive/**"`: no matches.
- `python3 -B -m pytest tests/test_visual_tokens.py tests/test_pyside6_style_adapter.py`: 58 passed.
- `git diff --check`: to be run before slice closeout.
- `git status --short`: to be run before slice closeout.

## Next

Slice 3 - Predict shell / command bar / status surface parity.

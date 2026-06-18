# 390 ResultPanel summary column width alignment

## Goal

Fix the Hong Kong CSPF/HSPF result summary where the first metric column was
visually narrower than the kWh columns after the calculator table bounded-width
layout correction.

## Scope

- Updated `ResultPanel` summary table column configuration to use a shared Tk
  grid `uniform` group for fields in the same summary card.
- Kept `content_hug` behavior: summary cards remain left-aligned and do not
  expand with the parent window.
- Added focused tests for:
  - uniform column policy in `ResultPanel`,
  - content-hug card width stability on window expansion,
  - Hong Kong CSPF/HSPF metric column alignment with kWh columns.

## Non-Goals

- No core/data/calculation changes.
- No Hong Kong CSPF/HSPF calculation or formatting value changes.
- No table controller, copy/paste, undo, or selection behavior changes.
- No Hong Kong-specific result table or new result framework.

## Result

Within each `ResultPanel` summary card, header/value columns now share equal
width while the card remains bounded to content width.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/result_panel.py`
- `python3 -B -m pytest tests/test_ui_tk_result_panel_stable_update.py -q`
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py -q`
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q`
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q`
- Manual smoke:
  - Window expansion does not over-stretch ISO/HK/EN14825 input/result tables.
  - Hong Kong CSPF/HSPF result table column width alignment has no visible issue.

Full final validation is recorded in the terminal closeout.

## Next

Manual smoke pending is closed. No follow-up is required for this result panel
column-width issue.

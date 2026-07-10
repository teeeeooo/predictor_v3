# Summary 654 - Calculator Maintenance And Micro-Polish Closeout

## Coverage

This summary closes completed active reports that landed after the Arc 13
feature catalog closeout and KOREA calculator sub-arc summary:

- `634_fix-table-font-en14825-header-width.md`
- `646_korea-midpoint-guide-recommended-capacity-fix.md`
- `652_delete-stale-iso-hspf-xlsm-audit.md`
- `653_calculator-micro-polish.md`

## Decisions And Outcomes

- Shared Tk calculator table typography was tightened to 10pt, with EN14825
  main table row headers widened only for the long EN14825 labels.
- KOREA midpoint guide recommended Mid capacity now reports the equivalent
  rated test-point capacity input, not the raw load at recommended tc.
- The stale ISO 16358 HSPF XLSM audit artifact was removed, and active
  documentation paths now point at current calculator owners under
  `core/calculators/standards/`.
- Calculator micro-polish before Arc 13.5 is complete: top-level calculator
  notebook tabs, ISO profile selector boundary, AHRI SEER2/HSPF2 action rows,
  and HSPF2 point display labels/order received UI-only polish with manual GUI
  smoke acceptance.

## Boundaries Preserved

- Calculator formulas, config semantics, public result keys, fixture/golden
  expected values, and schema/internal keys were not changed by the UI polish
  work.
- HSPF2 uses `H2v` and `H1N(STD)` only as visible UI labels; internal keys
  remain `H2Int` and `H1N`.
- The micro-polish branch was main-based and did not reuse or cherry-pick the
  discarded `feature/calculator-ui-polish` branch.

## Validation Evidence

- EN14825 focused Tk table tests passed for the typography/header-width slice.
- KOREA focused CSPF/HSPF usecase tests and broader KOREA calculator UI/detail
  smoke tests passed for the midpoint guide correction.
- Active documentation path scans and `git diff --check` passed for the stale
  XLSM audit removal.
- HSPF2/SEER2 focused Tk UI tests, batch spec tests, calculator foundation
  tests, compile checks, manual GUI smoke, merge readiness audit, and main
  fast-forward publication completed for the micro-polish slice.

## Memory Seed Sync Judgment

- Update the compact KOREA calculator seed entry with the midpoint guide
  recommended-capacity correction.
- Do not add a separate memory seed entry for the micro-polish UI work; it is
  covered by the existing calculator UI/application boundary entries and by
  `project_brief.md`.

## Next Action

- Resume Arc 13.5 Feature Catalog Editor work from the active planning report.

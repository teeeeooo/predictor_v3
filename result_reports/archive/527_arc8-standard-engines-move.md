# 527 Arc 8 Standard Engines Move

## Goal

Move calculator standard engine ownership under `core/calculators/standards/`
without changing formulas, behavior, or public classes.

## Moved Owners

- `core.calculators.standards.iso16358`: `ISO16358Calculator`.
- `core.calculators.standards.ks_c9306`: `KSC9306Calculator`.
- `core.calculators.standards.en14825`: `EN14825Calculator`.
- `core.calculators.standards.ahri_seer2`: `AHRICalculator`,
  `get_default_ahri_seer2_config`.
- `core.calculators.standards.ahri_hspf2`: `AHRIHSPF2Calculator`.
- `core.calculators.standards.asnzs_hspf_excel`:
  `ASNZSExcelHSPFCompatibilityCalculator`,
  `get_workbook_helper_column_map`, `get_workbook_output_anchor_map`.

## Compatibility

- Root `core/calculator_*.py` modules remain importable as compatibility
  wrappers.
- Dispatcher implementation now imports standard engines from
  `core.calculators.standards.*`.

## Excluded

- No formula, behavior, config, fixture, golden, public result key, calculator
  public class/function rename, ML, mapping schema, PySide6 recovery,
  worker/progress, Trainer, dependency, data/model artifact, or UI behavior
  changes.

## Verification

- Standard/root wrapper py_compile: passed.
- Root/new identity smokes for ISO16358, KS C 9306, EN14825, AHRI SEER2, AHRI
  HSPF2, and AS/NZS Excel compatibility: passed.
- Dispatcher profile smoke for `ks_c9306_cspf`: passed.
- New standards reverse-wrapper search: no matches.
- `git diff --check`: passed.
- `git status --short`: checked.

## Next Action

Slice 5 - Focused calculator tests, caller classification, and code map refresh.

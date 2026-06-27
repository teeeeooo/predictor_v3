# 483 Share Detail Formatting Coercion

## Goal

Extract only the repeated detail `_number` / `_text` coercion behavior into a
small pure helper while keeping every profile's field mapping, labels, schema,
and precision choices local.

## Changed Files

- `apps/calculator/ui/sections/detail_formatting.py`
- `apps/calculator/ui/sections/en14825_seer_detail.py`
- `apps/calculator/ui/sections/en14825_scop_detail.py`
- `apps/calculator/ui/sections/ahri_seer2_detail.py`
- `apps/calculator/ui/sections/ahri_hspf2_detail.py`
- `tests/test_ui_tk_en14825_seer_detail.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/483_share-detail-formatting-coercion.md`

## Changes

- Added `optional_fixed_number(value, precision)` and `optional_text(value)` as
  display-only primitive coercion helpers.
- Replaced the four duplicated formatter-local `_number` / `_text` functions
  with imports from the helper.
- Left all profile dictionaries, core-key to UI-key mappings, rounding
  precision call sites, and detail schemas unchanged.
- Added focused helper coverage for missing, invalid, and valid numeric/text
  values.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_en14825_seer_detail.py tests/test_ui_tk_en14825_scop_detail.py tests/test_ui_tk_ahri_seer2_detail.py tests/test_ui_tk_ahri_hspf2_detail.py` — passed, 21 tests.
- `python3 -B tools/code_checker/build_reference_map.py` — regenerated.
- `python3 -B tools/code_checker/build_reference_map.py --check` — fresh.
- `python3 -B tools/check_code_structure.py` — passed hard rules; existing EN
  section/adapter soft warnings remain.
- Final cached gate and diff check are run at slice closeout.

## Excluded Scope

- No generic row transformer was introduced.
- No field mapping, precision, label, detail payload, schema, core calculator,
  public API, fixture, or golden data changed.
- No lifecycle, panel, batch, or unrelated UI behavior changed.

## Reuse / Commonization Decision

Report 476 accepted only a pure coercion helper. This slice reuses the existing
four profile formatter owners for mapping and precision, and introduces one
section-local helper solely for the repeated missing/invalid/fixed-number/text
conversion policy. A generic schema-driven transformer remains rejected.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `result_reports/active/476_detail-formatting-helper-audit.md`: decision and
  implementation boundary, reason: preserve accepted helper scope.
- four detail formatter files: complete small files, reason: replace only
  duplicated coercion helpers while preserving profile mapping.
- four focused detail test files: formatter assertions, reason: preserve
  invalid/rounding behavior.
- broad read: none.
- repeated read: none.

## Next Action

Batch matrix controller implementation.

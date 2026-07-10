# 276 Extract Section-Level Result Formatting Helpers

## Goal

Move duplicated section-level helpers (`_bin_details`, `_metric_value`,
`_kwh_value`) from individual calculator section files into the shared
`ui_tk/sections/result_formatting.py` module.

## Scope

- `ui_tk/sections/result_formatting.py`: add public `bin_details`,
  `metric_value`, `kwh_value` helpers.
- `ui_tk/sections/hong_kong_cspf_section.py`: remove local `_bin_details`,
  import shared `bin_details`.
- `ui_tk/sections/iso_iseer_2point_section.py`: remove local `_bin_details`,
  `_metric_value`, `_kwh_value`; import shared helpers.
- `ui_tk/sections/iso_saso_t3_section.py`: remove local `_bin_details`,
  `_metric_value`, `_kwh_value`; import shared helpers.
- `tests/test_ui_tk_section_result_formatting.py`: add 10 focused tests.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: regenerate after structural
  helper extraction.

## Excluded Scope

- `hong_kong_hspf_section.py` (no duplicated helpers)
- Any table/controller/window/batch/core files
- Controller switch
- `BinDetailPanel` cleanup

## Reference Evidence Gate Usage

Per `docs/agent_workflows/DIFF_READ_BUDGET.md`:

- Map read: targeted `grep` on `_bin_details`, `_metric_value`, `_kwh_value`
  in `CODEBASE_REFERENCE_MAP.md` to confirm duplication.
- No broad map reads.
- Map regenerated after structural code changes (helper extraction).

## Extracted Helpers

**`bin_details(result) -> list[dict]`**

- Previously identical in 3 files.
- Returns `result["bin_details"]` as a list of dicts, or empty list.

**`metric_value(result, key) -> str`**

- Previously identical in 2 files.
- Returns `"-"` or `float(value):.3f`.

**`kwh_value(result, aliases) -> str`**

- Previously identical in 2 files.
- Returns `"-"` or `float(value):.1f` for the first matching alias.

## Behavior Compatibility

- Zero behavior change.
- `summarize_cspf_result` / `summarize_hspf_result` updated to use the new
  public `metric_value` instead of the removed `_metric_value`.
- Existing `_kwh_value` (with `kwh_aliases` / `wh_aliases` keyword-only args)
  is preserved for summary functions; the new public `kwh_value` is a thin
  wrapper for section call sites that use positional `aliases`.

## Tests

`tests/test_ui_tk_section_result_formatting.py` — 10 tests, all passing:

- `bin_details` list-of-dicts, missing, None, skip-non-mapping
- `metric_value` 3-decimal, dash-when-missing, zero
- `kwh_value` 1-decimal, first-alias-hit, dash-when-missing

## Code Map Regeneration Result

- Ran `python3 -B tools/code_checker/build_reference_map.py`.
- Duplicate section: `_bin_details`, `_metric_value`, `_kwh_value` no longer
  appear as multi-file duplicates.
- Map length: 226 lines (unchanged).

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Focused tests | `python3 -B -m pytest tests/test_ui_tk_section_result_formatting.py` | 10 passed |
| Code map regen | `python3 -B tools/code_checker/build_reference_map.py` | OK, 226 lines |
| Structural guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Compile check | `py_compile` on 4 modified files | OK |
| Git diff check | `git diff --check` | Clean |

## Modified Files

- `ui_tk/sections/result_formatting.py`
- `ui_tk/sections/hong_kong_cspf_section.py`
- `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/sections/iso_saso_t3_section.py`
- `tests/test_ui_tk_section_result_formatting.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Next

- `BinDetailPanel` cleanup preflight (split `__init__` / `_draw` long functions)
- Or controller switch design preflight for one pilot section

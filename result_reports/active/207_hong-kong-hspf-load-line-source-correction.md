# 207 — Hong Kong HSPF load-line source correction

## Goal

Correct Hong Kong HSPF so the heating load line uses measured 7 Full capacity instead of requiring an explicit rated heating capacity input.

## Preflight

- Current branch: `main`.
- Hong Kong CSPF still uses declared capacity for the CSPF load reference and was not changed.
- Hong Kong HSPF previously used `hspf.load_line.source = rated_heating_capacity`, which made the Tkinter UI require a rated heating capacity field.
- KS C 9306 HSPF uses the separate KS calculator path and keeps its `rated_cooling_capacity` load-line behavior.

## Modified Files

- `data/region_configs/hong_kong.json`
- `core/calculator_iso16358.py`
- `ui_tk/sections/hong_kong_hspf_section.py`
- `ui_tk/sections/iso16358_helpers.py`
- `tests/test_iso16358_hspf_hong_kong_config.py`
- `tests/test_iso16358_hspf_validation.py`
- `tests/test_ui_tk_iso16358_helpers.py`
- `tests/test_calculator_dispatcher.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `tests/test_ui_tk_iso_table_autocalc.py`

## Load-Line Source Change

Hong Kong HSPF config now declares:

- `source`: `measured_point_capacity`
- `point_key`: `7_full`
- `field`: `capacity`

`core/calculator_iso16358.py` now supports both existing `rated_heating_capacity` and new `measured_point_capacity` load-line sources. The rated source still requires a positive rated input. The measured source resolves the configured measured point and raises a clear `ValueError` when the point/field config or input is missing.

## UI Change

`HongKongHspfSection` no longer renders or reads the rated heating capacity table. The HSPF section calculates from 7 Full and 7 Half capacity/power inputs only. The existing Hong Kong CSPF declared-capacity table remains unchanged.

## Verification

- `python -m pytest -q tests/test_iso16358_hspf_hong_kong_config.py`: 10 passed
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py`: 25 passed
- `python -m pytest -q tests/test_iso16358_hspf_validation.py`: 37 passed
- `python -m pytest -q tests/test_iso16358_hspf_ks_oracle.py`: 2 passed
- `python -m pytest -q tests/test_calculator_dispatcher.py`: 15 passed
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py`: 8 passed, 36 skipped
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py`: 11 passed, 11 skipped
- `python3 -B tools/check_code_structure.py`: passed with existing soft-limit warning for `ui_tk/sections/bin_detail_panel.py`
- `git diff --check`: passed

## Manual Smoke Needed

- On Windows, open `app_calculator_tk.py`.
- Select Hong Kong HSPF.
- Confirm there is no rated heating capacity field.
- Confirm default 7 Full / 7 Half inputs calculate HSPF `3.643`.
- Confirm Hong Kong CSPF still shows and requires declared capacity.

## Excluded

- CSPF declared load reference changes.
- KS C 9306 HSPF load-line changes.
- Other region/profile HSPF changes.
- Batch UI correction.
- Detail/bin schema, graph/export, or internal formula trace work.

## Next Action

Run the Windows GUI smoke above, then continue with the planned calculator_tk follow-up work without mixing it into this HSPF correction.

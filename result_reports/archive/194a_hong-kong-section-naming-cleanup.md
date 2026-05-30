# 194-a Hong Kong Section Naming Cleanup

## Goal

Rename the existing Hong Kong CSPF/HSPF Tkinter section owners so the next Hong Kong CSPF trace slice has a clear home.

## Scope

- Renamed Hong Kong CSPF/HSPF section modules.
- Renamed their section classes.
- Updated `Iso16358Tab` imports and factory mapping.
- Updated focused code-structure guard test strings that referenced the old section names.
- No calculation, result rendering, layout, trace, CSV export, graph, or profile behavior was changed.

## Rename Result

- `ui_tk/sections/iso_cspf_section.py` -> `ui_tk/sections/hong_kong_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py` -> `ui_tk/sections/hong_kong_hspf_section.py`
- `IsoCspfSection` -> `HongKongCspfSection`
- `IsoHspfSection` -> `HongKongHspfSection`

## Reference Check

- Runtime use was limited to `ui_tk/tabs/iso16358_tab.py` Hong Kong metric factory mapping.
- `ui_tk` and `tests` no longer contain old class/module names.
- Full repository search still finds old names in historical docs/reports/archive entries. Those are past-record references and were not modified in this scoped rename.

## Verification

- `rg -n "IsoCspfSection|IsoHspfSection|iso_cspf_section|iso_hspf_section"`: old names remain only in historical docs/reports/archive entries outside this task scope.
- `rg -n "IsoCspfSection|IsoHspfSection|iso_cspf_section|iso_hspf_section" ui_tk tests`: no matches.
- `python3 -B tools/check_code_structure.py`: OK.
- `python3 -B -m py_compile ui_tk/sections/hong_kong_cspf_section.py ui_tk/sections/hong_kong_hspf_section.py ui_tk/tabs/iso16358_tab.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py tests/test_code_structure_guard.py`: OK.
- Quick smoke: `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_iso_hong_kong_sections_use_corrected_layout_without_action_buttons tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs`: 2 passed.
- Final focused: `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`: 64 passed.
- `git diff --check`: clean.
- Process check after verification: no lingering pytest process; only the check command and `rg` matched.

## Excluded Scope

- No Hong Kong CSPF trace implementation.
- No Hong Kong HSPF trace or heating schema implementation.
- No CSV export, graph, graph export, or HTML export changes.
- No `ResultPanel`, window geometry, scroll container, profile resolver, core/config/golden/fixture/PyQt changes.
- No lifecycle summary/archive, project log, or memory seed updates.

## Next Action

- `194-b Hong Kong CSPF bin trace implementation`

## Changed Files

- `ui_tk/sections/hong_kong_cspf_section.py`
- `ui_tk/sections/hong_kong_hspf_section.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_code_structure_guard.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/194a_hong-kong-section-naming-cleanup.md`

## Project Memory Delta

- none

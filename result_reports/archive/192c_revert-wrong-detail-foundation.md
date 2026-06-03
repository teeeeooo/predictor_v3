# 192-c Revert Wrong Detail Foundation

## Goal

Revert the 192-c input-point detail table foundation because it did not match the intended PyQt reference parity target.

## Reverted Commits

- `65e281d 192-c: document detail snapshot foundation`
- `679b027 192-c: add section result detail snapshots`

Reverted in reverse order with `git revert --no-edit`. No conflicts occurred.

## Reason

The 192-c implementation created a section-local `ResultSnapshot`, `DetailResultTable`, and collapsible detail pane that displayed input points plus summary values.

That was not the intended parity target. The relevant PyQt reference path is based on calculator `bin_details` and powers trace/detail/graph surfaces (`TraceTableModel`, `TraceDetailPanel`, `BinGraphWidget`). The input-point detail table is therefore likely unnecessary and could pollute the next structure if kept.

## Removed / Restored

Removed by revert:

- `ui_tk/sections/result_snapshot.py`
- `ui_tk/sections/detail_result_table.py`
- ISO/ISEER section snapshot/detail wiring.
- SASO T3 section snapshot/detail wiring.
- `Iso16358Tab` detail fit callback.
- 192-c detail/snapshot tests.
- Previous 192-c foundation report.

Restored / preserved:

- ISO/ISEER 2-point comparison table behavior.
- SASO T3 required-only and optional-min comparison behavior.
- Hong Kong `ResultPanel` path.
- Core/config/profile registry/golden/fixture state.
- No graph, bin-details trace table, internal formula trace, multi/batch, or EN/AHRI implementation.

## WORK_PLAN

`docs/WORK_PLAN.md` now records that the input-point 192-c foundation was reverted and sets the next action to:

- `PyQt bin_details trace/detail/graph parity audit`

## Verification

- `python3 -B tools/check_code_structure.py`: OK.
- Changed Python `py_compile`: OK for `tests/test_ui_tk_iso_table_autocalc.py`, `ui_tk/sections/iso_iseer_2point_section.py`, `ui_tk/sections/iso_saso_t3_section.py`, and `ui_tk/tabs/iso16358_tab.py`.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`: 51 passed.
- `git diff --check`: clean.
- Process check after verification: no lingering pytest process; only the check command itself matched.

## Next Action

Run a focused PyQt `bin_details` trace/detail/graph parity audit before implementing any new Tkinter result surface.

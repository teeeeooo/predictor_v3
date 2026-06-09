# 295 Summary - Controller Switch and ResultPanel Focus Preservation Arc (279-291)

## Covered Reports

Archived by this summary:

- `279_controller_switch_design_preflight.md`
- `280_metric_input_table_clipboard_protocol_compatibility_check.md`
- `281_controller_switch_parity_test_foundation.md`
- `282_fix_controller_parity_readonly_paste_test.md`
- `283_windows_parity_test_closeout.md`
- `284_controller_switch_pilot_implementation.md`
- `285_tk_table_controller_type_replace_flicker_diagnosis.md`
- `286_remove_redundant_focus_set_from_tk_table_controller_type_replace.md`
- `287_stable_result_panel_summary_update.md`
- `288_preserve_external_focus_during_result_panel_rebuild.md`
- `289_narrow_result_panel_focus_helper_exception_handling.md`
- `290_enforce_active_report_count_check.md`
- `291_close_out_post_focus_preservation_gui_smoke.md`

Also archived (related single completed items):

- `261_cleanup-duplicated-work-plan-next-actions.md`
- `263_metric-input-table-tktablesurface-adapter.md`
- `264_metric-input-table-visible-validation-foundation.md`

Reports intentionally kept active:

- `262_main-table-migration-candidate-check.md` — main table migration preflight result; migration not yet implemented.
- `274_ui_tk_cleanup_preflight.md` — ui_tk cleanup preflight result; cleanup not yet implemented.
- `275_code_quality_guardrail_backlog_registration.md` — backlog registered; processing not yet started.

## Arc Purpose

Migrate `HongKongCspfSection` from `ExcelLikeTableController` to the common `TkTableController` + `interaction_core.py` foundation, diagnose and fix ResultPanel flicker, resolve invalid text undo, and close out after GUI smoke.

## Completed Work

| # | Work | Status |
|---|---|---|
| 279 | Controller switch feasibility preflight | Design complete |
| 280 | MetricInputTable clipboard protocol compatibility check | Completed |
| 281 | Controller switch parity test foundation | Tests pass |
| 282 | Fix controller parity readonly paste test | Tests pass |
| 283 | Windows parity test closeout | Report-only |
| 284 | Controller switch pilot implementation for HongKongCspfSection | Implemented + 5 pilot tests |
| 285 | Flicker diagnosis — redundant `focus_set()` in `_type_replace` | Root cause identified |
| 286 | Remove redundant `focus_set()` from `TkTableController._type_replace` | Implemented + regression test |
| 287 | Stable ResultPanel summary update — same-shape in-place value/status update | Implemented + 9 tests |
| 288 | Preserve external focus during ResultPanel shape-change rebuild | Implemented + 4 focus tests |
| 289 | Narrow focus helper exception handling to `tk.TclError` | Cleanup complete |
| 290 | Enforce active report count check in agent output workflow | AGENTS.md / AGENT_TASK_ROUTER.md / RESULT_REPORT_WORKFLOW.md updated |
| 291 | GUI smoke closeout — iMac validation passed | Report-only |

## Key Decisions

- Controller switch is feasible; pilot implemented for HongKongCspfSection.
- Flicker root cause: redundant `focus_set()` in `TkTableController._type_replace`.
- Stable update: same-shape summaries update value/status text in place without widget destroy/recreate.
- Shape-change rebuild: external focus capture/restore via `_capture_external_focus()`, `_is_descendant_of_panel()`, `_restore_focus_if_alive()`.
- Exception handling: narrowed from broad `except Exception` to `except tk.TclError`.
- Active report count check: now enforced in AGENTS.md, AGENT_TASK_ROUTER.md, RESULT_REPORT_WORKFLOW.md.
- GUI smoke passed on iMac: flicker-free, invalid text undo restored, profile switch intact.

## Remaining Next Actions

- Controller switch expansion to remaining sections (HongKongHspfSection, IsoIseer2pointSection, SasoT3Section).
- Main table migration candidate check implementation (report 262, kept active).
- ui_tk cleanup implementation (report 274, kept active).
- Code quality guardrail backlog processing (report 275, kept active).

## Risks

- Controller switch expansion may reveal section-specific edge cases.
- `TkTableController` undo policy may need further refinement for non-numeric tables.
- ResultPanel stable update assumes field label order stability.

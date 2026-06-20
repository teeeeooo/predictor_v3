# 430 Implement AHRI HSPF2 Main UI Foundation

## Goal

Add the approved HSPF2 metric surface to the AHRI 210/240 calculator tab with
optional-point omission and hidden-default core mapping.

## Scope

- Add the HSPF2 adapter boundary, constants, options, parsing, unit conversion,
  optional omission, hidden defaults, and required result validation.
- Add the compact option bar, numeric options, A2 anchor, heating matrix, and
  HSPF2 result surface.
- Register HSPF2 beside SEER2 in the AHRI metric notebook.
- Add isolated temporary visual-smoke sample input and focused tests.

## Non-goals

- No HSPF2 batch or SEER2 main/batch behavior change.
- No core equation, config, schema, fixture, golden, EN14825, shared table,
  result, or batch framework change.
- No source-display detail or unrelated UI redesign.

## Changed Files

- `apps/calculator/ui/ahri/hspf2_adapter.py`
- `apps/calculator/ui/ahri/hspf2_mock_data.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `apps/calculator/ui/tabs/ahri210240_tab.py`
- `tests/test_apps_calculator_ui_ahri_hspf2.py`
- `tests/test_apps_calculator_ui_ahri_seer2.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/430_implement-ahri-hspf2-main-ui-foundation.md`

## Task Results

- AHRI metric order is SEER2 then HSPF2.
- HSPF2 defaults are Region IV; measured H42 on and H12/H22 off; H1N=H32 Hz
  off; MinSpd on; Cd 0.25; Defrost Credit 1.0; Cut Out/In -40.0°C.
- A2 is a separate two-field mini table and is never sourced from SEER2.
- Heating columns follow H01, H11, H1N, H2Int, H32, H42, H12, H22 with exact
  one-decimal Celsius labels.
- Inactive optional columns render read-only blank while retaining private UI
  text for later re-enable; the adapter omits their keys before core calling.
- The adapter converts Cut Out/In from visible Celsius to core Fahrenheit,
  injects defrost 90/720, and maps Cd, defrost credit, H1N, and MinSpd flags.
- Successful calculation renders one compact HSPF2 value and `자동 계산 완료`.

## Mock Data Lifecycle

- Temporary owner: `apps/calculator/ui/ahri/hspf2_mock_data.py`.
- The explicit symbol is `HSPF2_DEV_SAMPLE_VALUES`; no core, config, fixture,
  or golden file contains the sample.
- Removal: delete that file, remove its import from
  `ahri_hspf2_section.py`, and remove only the A2/heating sample-population
  loop in `_populate_initial_values`. Keep the numeric-option defaults.
- After removal the UI starts with empty A2/heating cells and blank result;
  widget structure, optional behavior, and adapter calculation remain intact.

## Table Parity Evidence

- All three input surfaces reuse `MetricInputTable` and `TkTableController`.
- Shared editable/read-only styling, clipboard, paste, clear, undo, navigation,
  and result presentation remain the common owners.
- Focused tests verify exact order/temperature, cell roles, optional toggling,
  A2 separation, hidden-field absence, and compact result status.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_hspf2.py tests/test_apps_calculator_ui_ahri_seer2.py`
  — initial run found one shared mock fan-out bug in four UI tests; after
  filtering sample values by each table's field order, 13 passed. A final
  test-only decoupling rerun also passed 13.
- `python3 -B tools/check_code_structure.py`
  — passed with two pre-existing EN14825 soft-LOC warnings and the
  pre-regeneration code-map stale reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check`, followed by
  regeneration because new production modules change indexed structure.
  — regenerated successfully.
- `git diff --check`
  — passed.
- `python3 -B tools/check_agent_change_gate.py --cached`

## Known Risks

- DEV sample data is intentionally visible until the calculator UI work is
  ready for the documented cleanup step.
- Platform-level sizing and keyboard smoke remains for the later AHRI lifecycle
  closeout; common controller behavior retains its existing test owners.
- `project_brief.md` is outside this task's explicit modification allow list;
  `docs/WORK_PLAN.md` is the synchronized current-slice owner.

## Scope Compliance

- New adapter, mock owner, and section files are each below 250 LOC.
- The existing SEER2 test change updates only the AHRI metric-tab expectation;
  no SEER2 implementation changed.
- No HSPF2 batch, SEER2 implementation, core, config, schema, fixture, golden,
  EN14825, or common framework file changed.

## Change Gate

```yaml
change_gate:
  new_source: split
  hotspot_delta: none
  code_map_check: regenerated
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed in this
  session; reason: applicable implementation gates.
- `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`:
  HSPF2 main layout, options, numeric inputs, A2, heating points, result,
  ownership, parity, and acceptance ranges; reason: approved contract.
- `core/calculator_ahri_hspf2.py`: production entrypoint, required canonical
  points, kwargs, optional resolution, and result return ranges only; reason:
  thin adapter mapping without core changes.
- Existing AHRI SEER2 adapter, section, and tab: corresponding composition and
  result patterns only; reason: reference parity.
- Existing HSPF2 focused core tests: canonical input and kwargs examples only;
  reason: confirm current public calling contract.
- `MetricInputTable` read-only presentation and controller refresh ranges;
  reason: optional column behavior through common components.
- `docs/WORK_PLAN.md`: current slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 main UI polish or AHRI HSPF2 batch design/implementation decision.

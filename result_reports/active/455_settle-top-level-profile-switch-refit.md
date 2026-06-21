# 455 Settle Top-Level Profile-Switch Refit

## Goal

Prevent an intermittent positive-but-undermeasured EN14825 window after
returning from another top-level calculator profile, without replacing the
immediate sizing path or introducing profile-specific geometry constants.

## Scope

- Compare top-level profile selection with EN14825 nested metric selection.
- Add an optional selected-tab visibility hook after the existing immediate fit.
- Make EN14825 request its existing coalesced refit with two settle cycles.
- Cover hook ordering, settle-cycle selection, positive geometry, and existing
  SEER/SCOP detail behavior with focused tests.

## Non-goals

- No negative-geometry guard change, common measurement arithmetic change,
  fixed geometry, profile minimum size, core/config/data/schema/fixture/golden,
  detail payload, sample data, batch, or AHRI SEER2 implementation change.

## Root Cause

EN14825 nested SEER/SCOP changes already request a refit through
`DynamicContentRefitScheduler`, allowing notebook content to settle before the
final measurement. In contrast, `CalculatorTkApp._on_tab_changed()` applied the
selected profile's preferred size and one immediate fit only. On an intermittent
Tk timing path, EN14825 could therefore be measured at a small but valid positive
size while its selected SEER detail surface was still settling. The 454 lower
bound correctly prevented a crash but could not distinguish that valid-looking
undermeasurement.

## Task Results

- `CalculatorTkApp` retains the existing preferred-size and immediate-fit order.
  It then calls `on_parent_tab_selected()` only when the selected tab provides
  that optional callable capability.
- `En14825Tab.on_parent_tab_selected()` requests the existing visible-lifecycle
  refit with `settle_cycles=2`.
- The existing scheduler continues to coalesce pending requests and suppress
  recursive measurement-triggered requests; no new scheduler behavior or forced
  interface was added.
- ISO and AHRI tabs do not implement the optional hook, so their top-level switch
  behavior remains unchanged.

## Verification

- EN14825 profile-switch lifecycle suite — 4 passed.
- EN14825 SEER/SCOP detail suite — 9 passed.
- `python3 -B tools/check_code_structure.py` — no errors; four known soft
  warnings only.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale from
  prior commit metadata; regenerated once.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Regression Contracts

- Existing immediate sizing precedes the optional settled-refit hook.
- EN14825 parent selection requests exactly two settle cycles.
- The existing negative-geometry profile-switch regression remains covered.
- SEER detail visibility still requests its ordinary one-cycle lifecycle refit.
- SEER/SCOP detail source, status, export, and table contracts remain unchanged.

## Manual Check

Required: open EN14825 SEER detail, switch to AHRI HSPF2 and open its detail,
return to EN14825 repeatedly, and confirm the SEER detail window settles to its
full visible-content height without compact undermeasurement or geometry jumps.

## Changed Files

- `apps/calculator/ui/calculator_app.py`
- `apps/calculator/ui/tabs/en14825_tab.py`
- `tests/test_ui_tk_en14825_profile_switch_fit.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/455_settle-top-level-profile-switch-refit.md`

## Known Risk

The original symptom is intermittent and macOS timing dependent. Contract tests
lock the scheduling boundary and ordering, while final visual confirmation still
requires the reported local profile-switch sequence.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed; reason:
  implementation, validation, and report boundaries.
- `calculator_app.py`, EN14825 tab, `window_refit.py`, and measurement references:
  selected lifecycle ranges only; reason: compare immediate and settled flows.
- EN14825 profile-switch and detail tests: focused lifecycle ranges; reason:
  regression contracts.
- `docs/WORK_PLAN.md`: current/next sections; reason: execution-board sync.
- broad read: none
- repeated read: none

## Next Action

EN14825 profile-switch visual smoke, then AHRI SEER2 detail view implementation.

# 434 Correct AHRI Visible-Content Refit Lifecycle

## Goal

Correct AHRI SEER2/HSPF2 root-window sizing by preventing hidden or unsettled
metric surfaces from initiating a content-hugging fit.

## Scope

- Gate AHRI metric refit requests on the selected top-level AHRI surface.
- Route visible metric changes through a settled lifecycle refit.
- Add focused hidden, visible, settle-cycle, and request-coalescing tests.
- Advance the near-term work-plan pointer.

## Non-goals

- No fixed geometry/minsize, table dimensions, calculator logic, A2 contract,
  source label, batch header, EN14825/ISO, or shared window-framework change.

## Changed Files

- `apps/calculator/ui/tabs/ahri210240_tab.py`
- `tests/test_ui_tk_ahri_window_refit.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/434_correct-ahri-visible-content-refit-lifecycle.md`

## Task Results

- Hidden AHRI metric-change events no longer request root-window refits.
- AHRI nested-notebook measurement is active only while the top-level AHRI tab
  is selected, preventing hidden construction snapshots from entering a fit.
- Visible SEER2/HSPF2 changes request one refit after two settle cycles; repeated
  events remain coalesced by the existing scheduler.
- The correction remains AHRI profile-local and uses the established snapshot
  provider and scheduler without changing common window policy.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_ahri_window_refit.py` — 3 passed.
  The first harness version used broad `root.update()` and was interrupted
  after two tests because unrelated UI idle callbacks prevented deterministic
  drain; the test was narrowed to advance only the scheduler settle stages.
- `python3 -B tools/check_code_structure.py` — passed with only two pre-existing
  EN14825 soft-LOC warnings and the expected code-map metadata reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale only
  by generated parent-SHA/dirty-tree metadata. No production file or top-level
  symbol structure changed, so regeneration was not required.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed after the
  report-only `new_source` evidence value was corrected to the allowed `small`.

## Manual Check Required

- AHRI SEER2 and HSPF2 do not retain excessive lower white space.
- SEER2/HSPF2 switching does not jump the main-window geometry.
- HSPF2 Batch open/close does not resize the main window.
- EN14825 SEER/SCOP sizing remains unchanged.

## Known Risks

- Exact window-manager geometry and visual white-space behavior require the
  requested local GUI smoke; automated tests cover request ownership and
  lifecycle ordering rather than pixel layout.

## Scope Compliance

- No width token, geometry constant, shared refit owner, or non-AHRI surface
  changed.
- The prompt-supplied owner boundary plus the established 233B/233C policy was
  sufficient; no unresolved design branch required a separate design gate.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed this
  session; reason: applicable implementation gates.
- `result_reports/memory/project_memory_seed.md`: 233/window-refit topic only;
  reason: locate superseding visible-snapshot lifecycle evidence.
- `result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md`:
  completed work and decisions only; reason: 233B/233C policy summary.
- `apps/calculator/ui/tabs/ahri210240_tab.py`: complete small target file;
  reason: profile-local request and measurement activation owner.
- `apps/calculator/ui/window_refit.py`, `window_measurement.py`: scheduler and
  nested snapshot ranges only; reason: settle/coalescing contract.
- ISO/EN tab lifecycle methods and focused window tests: matching ranges only;
  reason: reference parity without modification.
- `docs/WORK_PLAN.md`: current slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 A2 capacity-only and source mapping polish.

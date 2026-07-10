# 436 Reject AHRI Direct Metric Surface Sizing

## Goal

Test whether removing AHRI metric wrapper frames resolves the lower-white-space
regression without changing common window policy or calculator behavior.

## Scope

- Temporarily register the SEER2/HSPF2 section roots directly as notebook tabs,
  matching the ISO Hong Kong construction pattern.
- Re-run the existing sizing and refit diagnostics.
- Retain the production change only if the nested height gap improves.

## Non-goals

- No common window framework, fixed geometry/minsize, table dimensions/tokens,
  calculator/adapter, batch, A2/source, EN14825/ISO, core/config/fixture/golden,
  or unrelated refactor change.

## Final Changed Files

- `tests/test_ui_tk_visible_sizing_diagnostics.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/436_reject-ahri-direct-metric-surface-sizing.md`

`apps/calculator/ui/tabs/ahri210240_tab.py` was changed for the trial and then
restored exactly because the acceptance metric did not improve.

## Trial Result

The direct-section construction removed only the wrapper's 8px padding. It did
not change the height gap or contaminated chrome estimate.

| AHRI state | 435 baseline current/notebook | Direct surface current/notebook | Baseline gap | Direct gap |
|---|---:|---:|---:|---:|
| SEER2 | 332 / 697 | 324 / 689 | 365 | 365 |
| HSPF2 | 635 / 697 | 627 / 689 | 62 | 62 |
| SEER2 return | 332 / 697 | 324 / 689 | 365 | 365 |

SEER2 snapshot/root targets changed from 999x723 to 991x715, exactly the 8px
wrapper delta. `chrome_height_estimate` remained 365, overflow remained 44,
round-trip snapshots remained stable, and HSPF2 Batch open/close did not alter
main-window geometry.

## Correction Judgment

- **Wrapper hypothesis: rejected.** The wrapper is not the source of the
  303px SEER2/HSPF2 child-height difference embedded in the notebook request.
- **Production trial: reverted.** Keeping it would add structural churn without
  resolving the user-visible issue.
- **435 root cause: remains open.** The owner is the nested notebook requested-
  size/chrome-measurement interaction, not AHRI section nesting.
- **434: keep.** Visibility gating and settled scheduling remain correct and
  independent of this rejected structure hypothesis.

The next AHRI correction must explicitly address selected-child notebook
allocation and chrome derivation. Because this would cross into the common
measurement owner that this slice forbade, it needs a separate design/approval
slice rather than another profile-local patch.

## Diagnostic Update

The focused collector now emits `nested_height_gap` and asserts that AHRI SEER2
has a larger gap than EN SEER, that the gap is stable after the AHRI round trip,
and that Batch open/close preserves root geometry.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_visible_sizing_diagnostics.py tests/test_ui_tk_ahri_window_refit.py`
  — 4 passed on the final restored production tree.
- `python3 -B tools/check_code_structure.py` — passed with only two pre-existing
  EN14825 soft-LOC warnings and the existing code-map freshness reminder.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Manual Check

Required if a future correction is implemented: AHRI SEER2/HSPF2 lower space,
metric-switch geometry, HSPF2 Batch open/close, and EN14825/ISO regression. No
new visual smoke can accept this rejected hypothesis because no production
change remains.

## Known Risks

- AHRI lower white space remains unresolved.
- The current diagnostics prove the owner boundary but do not yet prescribe a
  platform-neutral notebook allocation API.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed this
  session; reason: applicable implementation/report gates.
- `result_reports/active/435_diagnose-en14825-vs-ahri-visible-sizing.md`:
  diagnostic table, root cause, and proposal only; reason: acceptance baseline.
- AHRI tab and SEER2/HSPF2 section construction ranges only; reason: direct
  section-root feasibility and lifecycle preservation.
- ISO Hong Kong metric construction range only; reason: requested direct-tab
  reference pattern.
- focused AHRI sizing diagnostic/window tests: complete small files; reason:
  before/after measurements and lifecycle regression.
- `docs/WORK_PLAN.md`: current-slice range; reason: rejected-hypothesis/next sync.
- broad read: none
- repeated read: none

## Next Action

Project-wide magic literal/token gate foundation.

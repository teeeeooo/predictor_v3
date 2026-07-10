# 190-a SASO T3 Design And Docs Cleanup

Date: 2026-05-30

## Goal

Perform docs-only cleanup after 189-e, add a small token/read-budget amendment, and complete a SASO T3 design slice.

## Changed Files

- `result_reports/active/189e_profile-switch-default-exact-fit-hotfix.md`
- `docs/WORK_PLAN.md`
- `AGENT_TASK_ROUTER.md`
- `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md`
- `result_reports/active/190a_saso-t3-design-and-docs-cleanup.md`

## 189-e Cleanup

- Updated 189-e report commit/push status:
  - source/test commit: `bcdb12a`
  - docs/report commit: `e516e30`
  - push: completed
- Converted manual check section to completed result based on user confirmation.
- WORK_PLAN 189-e checkpoint now reflects manual smoke completion and moving on.

## Token / Read Budget Amendment

- Added a small policy-section reuse hook to the existing `Diff / Read Budget`.
- Added one UI smoke-loop line to prefer cached policy context and short target-function reads.
- No new large Token Budget section or skill was added.

## SASO T3 Audit Summary

Checked:

- `app_calculator.py`
- `ui/calc_window.py`
- `ui/calculators_2point.py`
- `core/calculator_profiles.py`
- `data/region_configs/saso.json`
- `ui_tk/profile_resolver.py`
- `ui_tk/tabs/iso16358_tab.py`
- current Tkinter 2-point/result surfaces

Findings:

- `saso_t3_cspf` profile and `saso.json` already exist.
- PyQt reference uses required inputs `46 Full`, `35 Full`, `35 Half` and optional `35 Min`.
- PyQt result is a single SASO row/summary, not a two-profile comparison.
- Tkinter currently has no SASO mode label or section.

## Candidate Summary

- Candidate A: Add `SASO T3` selector mode and dedicated SASO section.
- Candidate B: Extend existing ISO/ISEER 2-point section.
- Candidate C: Extract a shared 2-point/SASO base before SASO.

Recommendation: Candidate A.

Reason: SASO has distinct input shape and optional min behavior, while a dedicated section keeps the implementation small and avoids regressions in ISO/ISEER 2-point and Hong Kong.

## Next Suggested Action

`190-b SASO T3 implementation slice`.

## Excluded Scope

- No Python source/test changes.
- No SASO implementation.
- No core/profile/config/golden/fixture/PyQt changes.
- No multi/batch/detail/graph/EN/AHRI.
- No project log, memory seed, summary, or archive changes.

## Verification

- `python3 -B tools/check_code_structure.py` -> OK
- `git diff --check` -> OK
- `git status --short`, `git diff --name-only`, `git diff --stat` reviewed before commit

## Project Memory Delta

- none

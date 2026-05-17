# 052 ISO Separation Completion Audit

## Goal

User objective completion audit for the `iso_seperation_plan.md` calculator series reset.

## Checklist

- `AGENTS.md` read and applied: yes.
- New branch used: yes, `work/iso-separation-plan`.
- `iso_seperation_plan.md` followed: yes, Steps 1-5 completed.
- Intermediate commits/pushes: yes, source/docs commits and report commits were pushed through `b0e7368`.
- `result_reports` and `project_log.md` updated: yes, reports 044-051 and corresponding log entries.
- Docs/data updated when needed: docs updated; no `data/region_configs/*.json` change was needed.
- Tests cleaned/deleted/archived when unnecessary: mixed/diagnostic legacy tests were moved to `tests/_legacy/`; no further tracked test deletion was made because remaining legacy-target tests preserve intentional golden/diagnostic coverage.
- Root Markdown result: `iso_separation_result.md`.

## Evidence

- `git status --short --branch`: clean after Step 5 push before this final audit work began.
- `tests/_legacy/` contains archived diagnostic/mixed legacy tests.
- Active UI/core/ASNZS guard paths no longer import `core.calculator_iso16358_legacy`.
- Latest full test run after Step 5: `280 passed, 16 failed, 13 xfailed`.

## Remaining Risk

- Known ISO HSPF 16-failure baseline remains unresolved by design.
- UI was not interactively smoked.
- Historical AS/NZS case3 full-dump parity remains Z-phase.

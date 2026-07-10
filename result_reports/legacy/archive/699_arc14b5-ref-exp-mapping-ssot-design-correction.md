# Arc 14B-5A Ref/Exp Mapping SSOT Design Correction

## Goal

Close the Arc 14B-5A open question for Refrigerant and Expansion options.

## Scope

- Updated the Arc 14B-5A design note to make `mapping.json` the SSOT for
  Refrigerant and Expansion.
- Updated `docs/WORK_PLAN.md` so the next implementation slice does not keep
  legacy fallback behavior.
- Added this compact result report.

## Design Decision

- Refrigerant projects to the required `ref_type` section.
- Expansion projects to the required `exp_type` section.
- Predict dropdowns must read `ref_type` and `exp_type` from `mapping.json`
  only.
- Hard-coded `FALLBACK_DROPDOWN_OPTIONS` behavior is legacy behavior and should
  be removed in implementation.
- Missing or empty `ref_type` / `exp_type` sections should be validation issues.

## Changed Files

- `docs/designs/2026-07-05-arc14b5-data-mapping-ui-crud-workflow-design.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/699_arc14b5-ref-exp-mapping-ssot-design-correction.md`

## Verification

- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: OK with 11 existing soft warnings
  unrelated to this docs/report-only slice.
- `git status --short`: expected changes only:
  - `docs/WORK_PLAN.md`
  - `docs/designs/2026-07-05-arc14b5-data-mapping-ui-crud-workflow-design.md`
  - `result_reports/active/699_arc14b5-ref-exp-mapping-ssot-design-correction.md`

`py_compile` and `pytest` were not run because this task changes docs/report
only and production code/tests/data fixtures remain untouched.

## Known Risks

- Production behavior is not changed in this slice. The actual fallback removal
  remains for the implementation slice.

## Commit / Push

- Source/docs commit: `b93ac3020848d6755e8485e2f7f1fe28091a4d55`.
- Final report commit and push verification are reported in the terminal/final
  response to avoid a self-referential report hash update loop.

## Next Action

Arc 14B-5B - implement editor draft projection from runtime `mapping.json` to
the seven user-facing groups in read-only mode, including `ref_type` /
`exp_type` mapping ownership and Predict dropdown fallback removal.

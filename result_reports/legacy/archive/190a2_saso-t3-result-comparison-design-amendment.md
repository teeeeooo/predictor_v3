# 190-a2 SASO T3 Result Comparison Design Amendment

Date: 2026-05-30

## Goal

Amend the 190-a SASO T3 design so SASO results compare required-only 3-point vs optional-min 4-point scenarios instead of showing only one single summary.

## Changed Files

- `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/190a2_saso-t3-result-comparison-design-amendment.md`

## Design Decision

Kept:

- `SASO T3` remains a dedicated Tkinter section.
- `SASO T3` remains an ISO profile selector option.
- Existing `saso_t3_cspf` profile/config remains the source.
- No core/config/golden changes.

Amended:

- SASO result display is a section-local comparison surface.
- Rows compare `Required only (3-point)` and `With 35 Min (4-point)`.
- Columns are `Scenario`, EER points, `CSPF`, `CSTL [kWh]`, `CSEC [kWh]`.
- Toggle off shows required-only result only.
- Toggle on + valid `35 Min` shows both rows.
- Toggle on + invalid/incomplete `35 Min` can keep the 3-point result while the 4-point scenario shows safe status/error.

## 190-b Scope Update

`190-b SASO T3 implementation slice` should include:

- `IsoSasoT3Section`
- optional `35 Min` toggle
- section-local SASO result comparison table
- 3-point and 4-point calculation paths from `saso_t3_cspf`
- no shared `ResultPanel` comparison mode or generic framework extraction

## Excluded Scope

- No source/test changes in this design amendment.
- No SASO implementation.
- No multi/batch/detail/graph/EN/AHRI.
- No core/profile/config/golden/PyQt changes.
- No project log, memory seed, summary, or archive changes.

## Verification

- `python3 -B tools/check_code_structure.py` -> OK
- `git diff --check` -> OK
- `git status --short`, `git diff --name-only`, `git diff --stat` reviewed before commit

## Project Memory Delta

- none

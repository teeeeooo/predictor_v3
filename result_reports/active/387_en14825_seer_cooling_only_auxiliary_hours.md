# 387 EN14825 SEER Cooling-Only Auxiliary Hours

## Goal

Implement cooling-only auxiliary operating hours for EN14825 SEER while
preserving existing reversible/default SEER results and SCOP
reversible/heating-only behavior.

## Scope

- Added SEER cooling operational-hours resolver in
  `core/calculator_en14825.py`.
- Extended `calculate_seer()` with a backward-compatible keyword-only
  `appliance_type="reversible"` parameter.
- Passed SEER appliance type through `SeerAdapter`.
- Removed appliance type ownership from EN14825 common numeric input.
- Added independent SEER and SCOP appliance selectors:
  - SEER: `reversible`, `cooling_only`;
  - SCOP: `reversible`, `heating_only`.
- Added focused core/adapter/UI tests.

## Non-goals

- No SCOP core behavior or SCOP config changes.
- No fixture/golden expected changes.
- No result key/schema changes.
- No unrelated refactor or lifecycle cleanup.

## Official / Design Basis

- Report 386 confirmed that active equivalent hours do not differ by appliance
  type within the same function, but auxiliary hours do.
- SEER reversible hours preserve the existing constants:
  `HCE=350`, `HTO=221`, `HSB=2142`, `HCK=2672`, `HOFF=0`.
- SEER cooling-only hours use the official values:
  `HCE=350`, `HTO=221`, `HSB=2142`, `HCK=7760`, `HOFF=5088`.

## Task Results

- Default `calculate_seer()` remains reversible and produces the existing
  golden result.
- `calculate_seer(..., appliance_type="reversible")` matches default.
- `calculate_seer(..., appliance_type="cooling_only")` applies larger
  auxiliary hours; with nonzero `Poff/Pck`, cooling-only SEER is lower than
  reversible.
- Invalid SEER appliance type raises `ValueError`.
- SEER adapter forwards `appliance_type` to core for declared/tested paths.
- EN14825 common input table now owns only Pto/Psb/Pck/Poff.
- SEER and SCOP appliance selectors are independent, preventing `cooling_only`
  from becoming a SCOP input.

## Verification

- `python3 -B -m py_compile core/calculator_en14825.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/en14825/seer_adapter.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/tabs/en14825_tab.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_seer_section.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m pytest tests/test_en14825_golden.py -q` OK, 7 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q` OK, 18 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 24 passed.
- `python3 -B tools/check_code_structure.py` OK with soft LOC warnings.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Structure Warnings

- `apps/calculator/ui/sections/en14825_seer_section.py` exceeds the 400 LOC
  soft limit after the selector addition.
- `apps/calculator/ui/sections/en14825_scop_section.py` continues to exceed the
  400 LOC soft limit.

## Warning Triage

- Reason: this slice adds narrow selector state and scheduling to existing
  section owners so the UI contract stays explicit and calculator behavior is
  preserved. It does not introduce new table/controller/helper abstractions.
- Action: accepted for this slice with reason.
- Follow-up: before adding more SEER or SCOP section UI responsibility, run a
  split audit or extract section subcomponents.

## Known Risks / Gaps

- Manual desktop smoke has not yet verified the new selectors visually.
- `calculate_seer()` still returns the existing public keys only; operational
  hours are intentionally not exposed in the result schema.

## Next Suggested Action

- Manual smoke EN14825 SEER reversible/cooling_only and SCOP
  reversible/heating_only selector behavior on the target desktop.

## Scope Compliance

- `data/region_configs/en14825_scop.json`, fixtures, golden expected values,
  memory/summary/archive, and workflow/architecture/UI-UX docs were not
  modified.
- SCOP core calculation behavior was not changed.

## Project Memory Delta

- none

## Commit / Push

- Final commit hash and push status are reported in terminal output.

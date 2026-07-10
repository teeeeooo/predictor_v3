# 306 Align 305 Code Checker Audit with Original Intent

## Goal

Compare and align the findings of the 305 code checker audit with the original design intent established in reports 270, 271, and 272. Clarify that `tools/code_checker` serves as a reference evidence map rather than a structural linter gate, and reorder the proposed follow-up slices.

## Scope

- Review reports 270, 271, and 272 to extract original design intents and constraints for `tools/code_checker`.
- Edit `result_reports/active/305_code_checker_and_reference_map_gate_audit.md` to align terminology and avoid over-extending `code_checker` into a semantic hard linter.
- Establish a corrected follow-up order prioritizing the SASO T3 input validation alignment.
- Update `docs/WORK_PLAN.md` and `project_log.md` to reflect the corrected next actions and choices.

## Evidence Read

- `result_reports/archive/270_code_checker_reference_map_foundation_design.md`
- `result_reports/archive/271_repo_reference_map_mvp_implementation.md`
- `result_reports/archive/272_repo_reference_map_calibration.md`
- `result_reports/active/305_code_checker_and_reference_map_gate_audit.md`
- `docs/agent_workflows/DIFF_READ_BUDGET.md`
- `AGENT_TASK_ROUTER.md`

## 270-272 Original Intent

- **Compact Reference Evidence Map**: Designed as a session-starter read aid to prevent redundant manual audits, locate symbol boundaries, and identify LOC hotspots.
- **Evidence, Not Source of Truth**: The map is treated as secondary context. The canonical rules remain in `AGENTS.md`, architecture docs, and `docs/WORK_PLAN.md`.
- **Relationship with Linter**: `tools/check_code_structure.py` is the structural linter with hard rules and exit codes. `code_checker` is specifically designed *not* to act as a compiler or blocking gate.
- **Explicit Exclusions**: Semantic clone detection, full call graphs, and CI/pre-commit hooks were explicitly excluded from the `code_checker` design to avoid bloat.

## 305 Audit Alignment

- 305 audit correctly identified critical gaps (map freshness, trigger subjectivity, semantic owner-bypass).
- However, proposing to integrate `code_checker` as a hard-fail/blocking warning gate in the pre-flight routine conflicted with the original intent (which delegates all hard checks to `check_code_structure.py` and leaves `code_checker` as a reference evidence generator).
- The definition of `code_checker` was corrected in 305 to ensure it remains a "reference/structure evidence map" rather than a "semantic analysis linter".

## Corrections Made

- **Report 305 Vocabulary**: Replaced references to `semantic analysis tool` with `reference/structure evidence map` (or symbol/import/hotspot evidence renderer) in the comparison section.
- **Report 305 Next & Slices**: Reordered the follow-up slices to put the immediate validation alignment first, rather than prioritizing map regeneration when the underlying section validation is still unaligned.
- **WORK_PLAN.md & project_log.md**: Corrected to set `SASO T3 Section Input Validation Alignment` as the immediate next action, keeping the code checker map refresh as a downstream action once the validation structures are stable.

## Corrected Follow-up Order

1. **SASO T3 Section Input Validation Alignment**
   - Align input parsing and visual error marking in `IsoSasoT3Section` with `MetricInputTable` standard path, keeping 35 Min fallback required-only behavior.
2. **Post-SASO T3 controller switch & validation GUI smoke**
   - Manual verification on iMac to verify controller switch and validation visual marking.
3. **Reference Evidence Gate semantic check patch**
   - Patch workflow docs to add warning-first semantic checklists (checking for owner-bypass, duplication, and hotspot expansion).
4. **code_checker metadata & freshness check improvement**
   - Make metadata task numbers flexible and improve freshness check options.
5. **Regenerate reference map and commit milestone changes**
   - Regenerate `docs/code_map/CODEBASE_REFERENCE_MAP.md` via `build_reference_map.py` to index CSPF, HSPF, 2-point, and SASO T3 switches.
6. **Main table migration check**
   - Assess common table convergence.
7. **ui_tk folder cleanup**
   - Refactor wrappers and duplicate helpers.

## Excluded Scope

- No modifications to code under `ui_tk/sections/` or `tools/`.
- No reference map regeneration.

## Active Report Count

- active report count exceeds lifecycle threshold; cleanup pending.

## Lifecycle Maintenance Note

- **Pending**: Deferred to a follow-up lifecycle cleanup slice after current audit/alignment steps are completed.

## Next

- SASO T3 Section Input Validation Alignment (Slice 1).

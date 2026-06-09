# 293 Summary - Code Checker Reference Map and Evidence Gate Arc (270-273)

## Covered Reports

Archived by this summary:

- `270_code_checker_reference_map_foundation_design.md`
- `271_repo_reference_map_mvp_implementation.md`
- `272_repo_reference_map_calibration.md`
- `273_reference_evidence_gate_read_budget_integration.md`

Reports intentionally kept active: none for this arc.

## Arc Purpose

Design and implement a lightweight `code_checker` reference map for the predictor_v3 codebase, then integrate it into the agent workflow as a conditional Reference Evidence Gate.

## Completed Work

| # | Work | Status |
|---|---|---|
| 270 | Code checker reference map foundation design | Design complete |
| 271 | Repo reference map MVP implementation | Implemented |
| 272 | Repo reference map calibration | Completed |
| 273 | Reference Evidence Gate integration into DIFF_READ_BUDGET.md | Workflow updated |

## Key Decisions

- `code_checker` provides machine-readable + human-readable codebase map to reduce repeated audits.
- `tools/check_code_structure.py` remains the structural linter; code_checker is a semantic map generator complement.
- Reference Evidence Gate is owned by `DIFF_READ_BUDGET.md` as a read-budget gate.
- Cross-references added to `AGENT_TASK_ROUTER.md` Shared Guardrails, Coding route, and UI route.

## Remaining Next Actions

- Code quality guardrail backlog processing (report 275, kept active).
- ui_tk cleanup implementation (report 274 preflight, kept active).

## Risks

- Map regeneration requires manual trigger; stale map risk remains if not regenerated after structural changes.
- Reference Evidence Gate effectiveness depends on map freshness.

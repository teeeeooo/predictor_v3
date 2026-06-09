# 305 Code Checker and Reference Map Gate Audit

## Goal

Audit `tools/code_checker` and the `CODEBASE_REFERENCE_MAP` workflows to assess how effectively they function as conditional quality gates, identifying capability gaps, freshness issues, and proposing follow-up alignment actions.

## Scope

- Review current capabilities and limits of `tools/code_checker/*` and `tools/check_code_structure.py`.
- Evaluate `CODEBASE_REFERENCE_MAP.md` update triggers and guidelines.
- Audit the integration of `Reference Evidence Gate` in `AGENT_TASK_ROUTER.md` and `docs/agent_workflows/DIFF_READ_BUDGET.md`.
- Classify structural and semantic gaps identified during recent controller switch implementations (such as local parsing bypassing common validation).
- Propose organized follow-up slices.

## Evidence Read

- `tools/code_checker/scanner.py`, `analyzer.py`, `build_reference_map.py`
- `tools/check_code_structure.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `AGENT_TASK_ROUTER.md` (Shared Guardrails, UI Section, Coding Section)
- `docs/agent_workflows/DIFF_READ_BUDGET.md` (Reference Evidence Gate section)
- `docs/REFACTOR_PLAN.md` (Code quality guardrail backlog)
- `docs/WORK_PLAN.md`
- `project_log.md` (recent reference map decisions)

## Current Code Checker Capability

The `tools/code_checker` framework provides a semantic and structure overview of the codebase:
- **Layer Overview**: High-level LOC counts and file distributions per top-level folder.
- **Keyword Hit Groups**: Fuzzy categorization mapping domain terms (`batch`, `table`, etc.) to files.
- **Hotspots (Active/Legacy)**: Identifies files exceeding size/complexity soft limits (LOC > 250, classes > 3, methods > 60 lines).
- **Duplicate Symbols**: Identifies duplicated classes, top-level functions, or constants across different files, filtering out standard framework terms.
- **Import Edges**: Captures package dependencies up to 3 levels deep to depict coupling.

**Comparison with `check_code_structure.py`**:
- `check_code_structure.py` is a **strict linter / enforcement gate** with hard checks (e.g., layer imports, thin app entries, hex-color policies) returning non-zero exit codes.
- `tools/code_checker` is a **semantic analysis tool** producing human/agent-readable documentation and is treated as *evidence* rather than a blocking compilation gate.

## Current Map Freshness Trigger

Currently, `CODEBASE_REFERENCE_MAP.md` defines its update trigger as:
> Update this map after significant architectural changes or before large migrations.

`docs/agent_workflows/DIFF_READ_BUDGET.md` defines regeneration as:
> Regenerate only after structural code changes (new files, moved files, new symbols, removed helpers).

**Identified Freshness Blocker**:
- The terms "significant" and "large" are highly subjective.
- Recent switch implementation tasks explicitly prohibited map regeneration in their prompts, creating a contradiction where structural changes occurred (e.g. migration to `TkTableController` across sections, adding focused tests) but the map was kept stale.

## Reference Evidence Gate Findings

The `Reference Evidence Gate` is integrated into the read budget workflow in `DIFF_READ_BUDGET.md`.
- **Strengths**: Successfully prevents agents from doing broad, context-wasting reads of the entire map by enforcing targeted regex/grep searches (`rg -n`).
- **Gaps**: The gate is currently a "read-only lookup". The agent checks if the file is in the map, but the workflow does not require verifying architectural compliance or looking out for:
  1. **Owner-bypass**: Overriding common table validation and writing localized parsers.
  2. **Duplication**: Adding redundant helpers that do the same as common routines.
  3. **Hotspot expansion**: Expanding files that are already flagged as hotspots without splitting.

## Project-wide Gaps

1. **Map Freshness Gap**: Structural changes (adding focused tests, changing controller imports) occur without updating the map, meaning subsequent agents read stale symbol indices.
2. **Workflow Trigger Gap**: Lack of precise automation to detect when a map is stale. There is no automated hook warning the agent that the map differs from the actual source code structure.
3. **Semantic Owner-Bypass Detection Gap**: Static analysis cannot detect when a section-level file (e.g., `IsoSasoT3Section`) bypasses a common component's responsibility (e.g. `MetricInputTable` validation) and writes custom logic (`_parse_positive`).
4. **Duplicate Responsibility Detection Gap**: `code_checker` only detects identical top-level symbol names. It does not detect duplicated inline behaviors or cloned logic blocks.
5. **Hotspot Responsibility Expansion Gap**: While files exceeding soft limits are marked as hotspots, there is no enforcement preventing agents from adding more lines to an active hotspot during small feature increments.

## Follow-up Slice Recommendations

To address these gaps systematically, the following sequential follow-up slices are proposed:

### Slice 1: CODEBASE_REFERENCE_MAP.md Regeneration & Milestone Commit (High Priority)
- **Goal**: Bring the reference map up to date with all recently completed controller switch migrations (CSPF, HSPF, 2-Point, SASO T3) and focused tests.
- **Scope**: Re-run `build_reference_map.py` and commit the updated map.
- **Verification**: Verify symbols, LOC, and hotspots accurately represent current state.

### Slice 2: Reference Evidence Gate Semantic Questionnaires Patch
- **Goal**: Patch the workflow documents to turn the Reference Evidence Gate from a simple "lookup" into a semantic check (e.g., check for duplication and owner-bypass before writing).
- **Scope**: Update `docs/agent_workflows/DIFF_READ_BUDGET.md` and `AGENT_TASK_ROUTER.md`.
- **Verification**: Structural check pass.

### Slice 3: Reference Map Freshness Automation & Warning-First Gate
- **Goal**: Integrate a quick freshness validation check into the pre-flight routine so the agent is warned when the source code structure has drifted from the committed map.
- **Scope**: Create `tools/check_reference_map_freshness.py` or extend `check_code_structure.py`.
- **Verification**: Run checker and verify warning triggers on structural diffs.

### Slice 4: SASO T3 Section Input Validation Alignment
- **Goal**: Refactor `IsoSasoT3Section` to align with the standard validation and error-marking semantics of `MetricInputTable`, eliminating localized input parsing and owner-bypass.
- **Scope**: `ui_tk/sections/iso_saso_t3_section.py`
- **Verification**: SASO T3 validation unit tests.

### Slice 5: Active Report Count Lifecycle Cleanup
- **Goal**: Archive current active reports (>10) into summary reports to restore codebase hygiene.
- **Scope**: Move reports from `result_reports/active/` to `result_reports/archive/` and generate summaries.
- **Verification**: Active report count <= 10.

## Excluded Scope

- No modifications to Python code, linters, or calculators in this audit task.
- No map regeneration or manual GUI verification performed.

## Active Report Count

- 13 active reports present (>10, cleanup pending).

## Lifecycle Maintenance Note

- **Pending**: Deferred to a follow-up lifecycle cleanup slice after current audit and next actions are integrated.

## Next

- Regenerate reference map and commit milestone changes (Slice 1).

# 192-a Tkinter Next Slice Selection Audit

## Current State

Tkinter ISO profile expansion arc is complete:

- `ISO / ISEER 2-point` default profile, comparison table, safe invalid handling.
- `Hong Kong` CSPF/HSPF metric sub-tabs remain unchanged.
- `SASO T3` dedicated section with required-only 3-point vs optional-min 4-point comparison, toggle, and manual smoke (190-b) — no issues found.
- WORK_PLAN compaction finished (191-b).

## Candidate Comparison

### A. SASO follow-up polish
- **Value**: Low. 190-b manual smoke found no concrete issues.
- **Risk**: Very low.
- **Design First**: Not required (hotfix scope).
- **Core/config/golden impact**: None.
- **Verdict**: Hold unless a concrete issue appears.

### B. Multi/batch design
- **Value**: Medium-high (repeated input + grouped results).
- **Risk**: Medium. Input repetition UI, result persistence, and memory/performance surface remain, but the UI can be a separate Toplevel window rather than embedding inside the existing ISO tab. This isolates it from the current ISO tab geometry and section structure.
- **Design First**: Required. Result structure, input-loop UI, and window lifecycle still need design.
- **Core/config/golden impact**: Low-medium; UI surface churn is isolated to the new window.
- **Verdict**: Deferred. Needs dedicated design slice later.

### C. Detail/trace/graph design
- **Value**: High. Enriches the already-complete single-calculation result experience.
- **Risk**: Medium. Needs explicit preferred-size ownership (191 summary flagged this). Core change not required.
- **Design First**: Required. Surface type, placement, and geometry impact must be decided before implementation.
- **Core/config/golden impact**: None in the design slice.
- **Verdict**: Recommended next design slice.

### D. EN/AHRI Tkinter expansion design
- **Value**: Medium (new standard coverage).
- **Risk**: High. New profile/config path, new calculator integration, wide tab/section footprint.
- **Design First**: Required.
- **Core/config/golden impact**: High. Likely touches profile registry and region configs.
- **Verdict**: Deferred. Too large and core-invasive for the current arc.

## Recommended Slice

**192-b detail/trace/graph design slice**

- **Purpose**: Design richer result surfaces (detail table, calculation trace, and/or graph) for the existing single-calculation ISO/ISEER 2-point and SASO T3 sections.
- **Audit scope**:
  - Current section-local read-only result tables (`IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`).
  - `iso16358_tab.py` preferred-size and geometry reset behavior.
  - UI/UX SSOT for dynamic surfaces (`docs/ui_ux/00_UI_UX_SYSTEM.md`, `03_SPREADSHEET_TABLE_UX_CONTRACT.md`).
- **Design decisions needed**:
  1. Surface placement: section-local embedded pane vs separate dialog/tab.
  2. Preferred-size owner when dynamic surfaces expand/contract after calculation.
  3. Trace/detail data contract: what does the UI layer need from the calculator result without changing core?
  4. Graph tooling: embedded matplotlib, generated image, or external window (policy in `01_TOOLKIT_SELECTION_POLICY.md`).
  5. Single-result mapping: how detail/trace/graph maps to comparison rows (ISO/ISEER 2-point multi-row, SASO 3-point vs 4-point).
- **Excluded scope**:
  - Core calculator, profile registry, region config, golden, fixture changes.
  - Multi/batch input or result persistence.
  - EN/AHRI expansion.
  - SASO follow-up polish.
  - Shared `ResultPanel` rewrite.

## Deferred Candidates

- **SASO follow-up polish**: No concrete issue after 190-b smoke. Hold.
- **Multi/batch**: High UI churn and result-structure risk. Needs its own design slice later.
- **EN/AHRI expansion**: High core/config footprint. Deferred until the current ISO arc stabilizes.

## Next Action

Proceed to **192-b detail/trace/graph design slice**.

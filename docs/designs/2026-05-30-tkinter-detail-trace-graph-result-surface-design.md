# Tkinter Detail / Trace / Graph Result Surface Design

## Background

The Tkinter ISO profile expansion arc (ISO/ISEER 2-point, Hong Kong, SASO T3) is complete. The current new result surfaces are section-local read-only comparison tables (`IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`). This design explores how to enrich those surfaces with detail, trace, and graph without modifying core/config/golden.

The PyQt reference app (`app_calculator.py` -> `ui/calculators_2point.py`) already has `TraceTableModel`, `BinGraphWidget`, and `TraceDetailPanel`. Those reference widgets use calculator `bin_details` as a bin-level trace table/graph source. That is a useful reference surface, but it is not the same as an internal formula trace.

## Current Result Surfaces

- **ISO/ISEER 2-point**: one comparison table with 1-2 rows (ISO 16358-1, India ISEER). `IsoIseer2PointSection` receives each raw `result` from `calculate_cspf()` during `recalculate_now()`, then formats and passes rows to `IsoIseer2PointResultTable`.
- **SASO T3**: one comparison table with 1-2 rows (Required-only 3-point, With 35 Min 4-point). `IsoSasoT3Section` receives each raw `result` from `calculate_cspf()`, then formats scenario rows for `IsoSasoT3ResultTable`.
- **Hong Kong**: `IsoCspfSection` / `IsoHspfSection` use the existing `ResultPanel` path with formatted `ResultSummary` objects. This design does not change that path.

Each table shows:
- Region/Profile or Scenario
- Per-point EER (capacity / power)
- CSPF/ISEER
- CSTL [kWh]
- CSEC [kWh]

## Available Result Data / Missing Data

### Available during section calculation (no core change)
- `measured` dict: per-point `capacity`, `power`.
- `result` dict: `cspf`, `annual_cooling_kwh` / `cstl_kwh` / `cstl`, `annual_power_kwh` / `csec_kwh` / `csec`.
- `result["bin_details"]` for CSPF profile calculations, with bin-level keys used by the PyQt reference trace/graph (`bin_no`, `tj`, `nj`, `lc`, `capacity`, `power`, `eer`, `cstl_bin`, `csec_bin`).
- `errors` (handled in section, not exposed as structured data).

### Available in the current rendered Tk surface
- Only formatted comparison rows and status text are retained in the table classes.
- Raw `measured`, raw `result`, and `bin_details` are not retained by a section-local result snapshot yet.

### Missing or not stable enough
- A normalized section-local result snapshot model that maps comparison rows to raw `measured`/`result` data.
- Internal formula trace contract: branch choices, formulas, interpolation decisions, degradation calculations, and assumptions are not exposed as a stable cross-profile UI contract. Some HSPF common-engine bin details include formula trace-like keys, but that is not a general CSPF/SASO/ISEER trace API.
- Graph surface sizing/tooling decisions.

## Surface Candidates

### 1. Detail table
- **What**: Expand the existing comparison row into a per-point detail view (capacity, power, EER/COP per point, plus annual energy totals).
- **Value**: High. Users can inspect every input point and derived metric in one place.
- **Current data fit**: Uses `measured` and summary keys from `result`; does not require `bin_details`.
- **Needed data contract**: Section-local retained snapshots keyed by row/scenario label.
- **Core change**: None.
- **Implementation size**: Small. New read-only Treeview/table inside the section, following the Tkinter read-only table adapter baseline.
- **Test**: Verify row count, cell values, valid/invalid inputs, and copy text if the detail table exposes clipboard support.

### 2. Calculation trace
- **Reference/bin trace**: PyQt uses `bin_details` as a trace table. For CSPF-based ISO/ISEER/SASO calculations this data is already present in the raw result, but the Tk sections do not retain it yet.
- **Internal formula trace**: Formula choices, interpolation branches, and derivation steps need a stable core/data contract before the UI should expose them as trace.
- **Value**: Medium. Bin trace is useful for audit/debug; formula trace is useful for deep verification.
- **Current data fit**: Bin trace is possible after section-local result snapshot retention. Formula trace is not ready.
- **Implementation size**: Medium for bin trace; medium-large for formula trace because it crosses UI/core boundaries.
- **Verdict**: Do not combine with the first detail implementation. Treat bin-details reference trace and internal formula trace as separate later decisions.

### 3. Graph
- **What**: Visualize EER/COP per point, load curve, or seasonal distribution.
- **Value**: Medium-high. Faster intuitive understanding than tables.
- **Current data fit**: Basic point plots can use `measured`; seasonal/bin graphs can use raw `result["bin_details"]` after snapshot retention.
- **Needed data contract**: Graph mode must declare whether it consumes input points, summary values, or bin details.
- **Core change**: None for CSPF point/bin graphs, but internal formula graphing would require a trace contract.
- **Implementation size**: Medium. Tooling, dependency footprint, export behavior, and preferred-size impact must be decided first.
- **Verdict**: Deferred to a dedicated graph slice after detail is stable.

### 4. Summary: what to implement first
- **First slice**: Detail table only.
- **Later slice**: Bin-details reference trace or graph, after section-local result snapshots exist.
- **Separate later slice**: Internal formula trace, after a core/data contract design.

## Placement Candidates

### A. Section-local collapsible secondary pane (recommended)
- A "자세히 보기 / 상세 결과" button or small toggle inside each section.
- When expanded, a detail table/frame packs below the comparison table.
- When collapsed, it pack_forgets and comparison table returns to full width.
- **Pros**:
  - Natural for single-calculation sections.
  - Profile switch already hides/shows the whole section; no extra lifecycle.
  - ScrollableFrame absorbs overflow without new dialogs.
- **Cons**:
  - Expanding detail changes content height → geometry impact unless managed.
- **Mitigation**: Default collapsed; user-initiated expand triggers one-shot fit via existing `_fit_toplevel_to_current_content`.

### B. Result table below section-local detail tabs
- Add a ttk.Notebook or tab-like row below the comparison table.
- **Pros**: Organized if many surface types coexist.
- **Cons**: ttk.Notebook inside a section adds geometry complexity and nested tab switching. Overkill for a single detail table.

### C. Separate detail dialog / Toplevel
- **Pros**: Zero geometry impact on the main ISO tab.
- **Cons**: Breaks the single-calculation flow. Mapping a dialog to comparison rows is awkward. Extra window management.

### D. App-level shared detail/graph window
- **Cons**: Violates the current section-local ownership principle. Requires shared framework design.

### Final placement recommendation
- **Option A**: section-local collapsible detail pane.
- Detail surface is owned by the section (`IsoIseer2PointSection`, `IsoSasoT3Section`).
- Collapse/expand is a section-local concern.
- Hong Kong (`ResultPanel`) is not affected.
- Do not introduce a shared result framework until another slice proves repeated reuse.

## Preferred-Size / Geometry Policy

Current policy (from `iso16358_tab.py` and `window_geometry.py`):
1. Render content.
2. Measure `winfo_reqwidth/height`.
3. Apply safety margin.
4. Screen cap.
5. Center.
6. One measured overflow correction.
7. Scroll reset.

For dynamic detail surfaces:
- **Do not** add a continuous `<Configure>` observer.
- **Do not** hardcode pixel sizes per surface state.
- **Allowed**: after a user-initiated expand/collapse, call `_fit_toplevel_to_current_content` once (same path as profile switch).
- **Preferred-size owner**: `iso16358_tab` remains the owner. The section simply includes the detail pane in its natural size when packed; `preferred_initial_size()` measures it automatically. The implementation can use a narrow callback/event from section to tab, but geometry mutation stays in the tab/window geometry path.
- **Default state**: collapsed (detail pane not packed) so the initial geometry is unchanged.
- **Scroll**: if the expanded content exceeds the viewport, ScrollableFrame scrollbar appears. No geometry mutation loop.

## Graph Tooling Decision

- **Tkinter policy**: stay on Tkinter. Do not introduce PyQt5 or mix widget toolkits.
- **Matplotlib embedded canvas**: viable for rich plots, but adds dependency and an embedded-canvas preferred-size surface.
- **Generated image displayed in Tk**: smaller UI contract and easier sizing/export, but less interactive and may add image-generation/storage decisions.
- **Separate image/export dialog**: isolates main-tab geometry, but introduces window lifecycle and export-state questions.
- **Defer graph**: lowest risk for the next slice; preserves the detail MVP and leaves dependency choice open.
- **Recommendation for this design**: **defer graph and do not choose a graph library yet**. The first slice is detail-table only. A later graph slice should choose data source (`measured` vs `bin_details`), toolkit, dependency footprint, and geometry owner together.

## Recommendation

1. **Next implementation slice**: `192-c section-local detail table MVP`.
   - Add a collapsible detail pane to `IsoIseer2PointSection` and `IsoSasoT3Section`.
   - Content: per-point capacity, power, EER/COP, plus annual energy summary.
   - Data source: retained section-local snapshots of existing `measured` and `result` dicts (no core change).
   - Default: collapsed.
   - Expand: user clicks a toggle/button; section packs the detail frame; one-shot window fit.
2. **Following design choice**: bin-details reference trace or graph, after detail MVP proves the snapshot/placement pattern.
3. **Separate future design**: internal formula trace, after a core/data contract proposal.

## Excluded Scope

- Core calculator, profile registry, region config, golden, fixture changes.
- Hong Kong `ResultPanel` modifications.
- Shared result surface framework.
- Multi/batch input or result persistence.
- EN/AHRI expansion.
- Graph dependency/import/code in the first slice.
- Internal formula trace UI.

## Risks / Open Questions

- **Dynamic geometry**: expanding detail on a small screen may hit the screen cap. Acceptable; scrollbar appears.
- **Multi-row mapping**: ISO/ISEER 2-point has two rows (ISO, ISEER). Detail pane should map to the selected/comparison row, or show both. Design decision in 192-c: show a single combined detail table for all rows, or a row selector.
- **SASO optional 35 Min**: detail pane must handle the optional point gracefully (show "-" when disabled).
- **Testability**: detail table is read-only; tests verify row count and cell text for known inputs.

## Design Gate Summary

### Goal
Decide the first safe result-surface expansion for Tkinter ISO/ISEER 2-point and SASO T3 without source changes in this design slice.

### Confirmed Decisions
- Start with a section-local collapsible detail table MVP.
- Keep Hong Kong `ResultPanel` unchanged.
- Keep graph and trace out of the first implementation slice.

### UI vs Core Boundary
- UI sections may retain raw `measured`/`result` snapshots they already receive.
- Core/config/golden/profile registry stay unchanged for 192-c.

### Data Shape / API Boundary
- 192-c uses existing `measured` plus summary keys from `result`.
- `bin_details` is available as a future reference trace/graph data source, but not required for the detail MVP.
- Internal formula trace requires a future core/data contract.

### Required Tests
- Focused Tk UI tests or smoke for detail collapse/expand, row labels, optional SASO 35 Min behavior, and no stale detail after invalid input.

### Migration / Refactor Path
- Add section-local detail only first.
- Consider a shared helper only after ISO/ISEER and SASO duplicate enough detail-table behavior to justify extraction.

### Risks
- Expanded content may hit the screen cap and rely on scroll.
- Row selection vs combined detail display must be chosen in 192-c before implementation.

### Non-goals
- Graph implementation, formula trace implementation, multi/batch, EN/AHRI, ResultPanel rewrite, and core/data changes.

### Next Codex Implementation Prompt
Implement `192-c section-local detail table MVP` for `IsoIseer2PointSection` and `IsoSasoT3Section` using retained section-local result snapshots, default-collapsed detail panes, and one-shot tab-owned fit on expand/collapse.

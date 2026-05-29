# Tkinter Detail / Trace / Graph Result Surface Design

## Background

The Tkinter ISO profile expansion arc (ISO/ISEER 2-point, Hong Kong, SASO T3) is complete. The current result surfaces are section-local read-only comparison tables (`IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`). This design explores how to enrich those surfaces with detail, trace, and graph without modifying core/config/golden.

## Current Result Surfaces

- **ISO/ISEER 2-point**: one comparison table with 1–2 rows (ISO 16358-1, India ISEER).
- **SASO T3**: one comparison table with 1–2 rows (Required-only 3-point, With 35 Min 4-point).
- **Hong Kong**: stays on the existing `ResultPanel` path; out of scope for this design.

Each table shows:
- Region/Profile or Scenario
- Per-point EER (capacity / power)
- CSPF/ISEER
- CSTL [kWh]
- CSEC [kWh]

## Available Result Data / Missing Data

### Available now (no core change)
- `measured` dict: per-point `capacity`, `power`.
- `result` dict: `cspf`, `annual_cooling_kwh` / `cstl_kwh` / `cstl`, `annual_power_kwh` / `csec_kwh` / `csec`.
- `errors` (handled in section, not exposed as structured data).

### Missing (needs future core/data contract)
- Bin-level weights, load hours, climate data.
- Intermediate calculation steps (trace).
- Seasonal performance breakdown beyond the current summary keys.

## Surface Candidates

### 1. Detail table
- **What**: Expand the existing comparison row into a per-point detail view (capacity, power, EER/COP per point, plus annual energy totals).
- **Value**: High. Users can inspect every input point and derived metric in one place.
- **Core change**: None. Uses `measured` and `result` already in the section.
- **Implementation size**: Small. New read-only table or Treeview inside the section.
- **Test**: Verify row count and cell values for valid/invalid inputs.

### 2. Calculation trace
- **What**: Show intermediate values (bin weights, load line intersection, degradation coefficient application, etc.).
- **Value**: Medium. Useful for debugging or regulatory submission.
- **Core change**: Required. The calculator must expose trace data in the result dict or a separate trace API.
- **Implementation size**: Medium-large, blocked on core contract.
- **Verdict**: Deferred to a future slice that includes core trace design.

### 3. Graph
- **What**: Visualize EER/COP per point, load curve, or seasonal distribution.
- **Value**: Medium-high. Faster intuitive understanding than tables.
- **Core change**: None for basic point plots; seasonal graphs need bin data (missing).
- **Toolkit**: Tkinter app stays on Tkinter. Matplotlib with TkAgg backend is acceptable per `01_TOOLKIT_SELECTION_POLICY.md` because it does not introduce PyQt5 and is a well-known Tkinter companion.
- **Implementation size**: Medium. Dependency decision, canvas embedding, and dynamic preferred-size impact.
- **Verdict**: Deferred to a dedicated graph slice after detail is stable.

### 4. Summary: what to implement first
- **First slice**: Detail table only.
- **Second slice**: Graph (after toolkit and data contract decisions).
- **Third slice**: Trace (after core trace data contract).

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
- **Preferred-size owner**: `iso16358_tab` remains the owner. The section simply includes the detail pane in its natural size when packed; `preferred_initial_size()` measures it automatically.
- **Default state**: collapsed (detail pane not packed) so the initial geometry is unchanged.
- **Scroll**: if the expanded content exceeds the viewport, ScrollableFrame scrollbar appears. No geometry mutation loop.

## Graph Tooling Decision

- **Tkinter policy**: stay on Tkinter. Do not introduce PyQt5.
- **Matplotlib**: acceptable companion for Tkinter (`FigureCanvasTkAgg`). It adds a dependency but does not violate the single-toolkit rule.
- **Pillow-generated image**: lighter, but static and non-interactive.
- **Recommendation for this design**: record matplotlib as the likely graph toolkit, but **do not implement graph in the first slice**. The first slice is detail-table only.
- Graph slice will need its own design decision on:
  - Dependency footprint (`matplotlib` vs lightweight alternative).
  - Interactive vs static.
  - Preferred-size impact of an embedded canvas.

## Recommendation

1. **Next implementation slice**: `192-c section-local detail table MVP`.
   - Add a collapsible detail pane to `IsoIseer2PointSection` and `IsoSasoT3Section`.
   - Content: per-point capacity, power, EER/COP, plus annual energy summary.
   - Data source: existing `measured` and `result` dicts (no core change).
   - Default: collapsed.
   - Expand: user clicks a toggle/button; section packs the detail frame; one-shot window fit.
2. **Following slice**: graph design/implementation (after detail MVP is stable).
3. **Following slice**: trace design (after core exposes trace data contract).

## Excluded Scope

- Core calculator, profile registry, region config, golden, fixture changes.
- Hong Kong `ResultPanel` modifications.
- Shared result surface framework.
- Multi/batch input or result persistence.
- EN/AHRI expansion.
- Matplotlib import or graph code in the first slice.

## Risks / Open Questions

- **Dynamic geometry**: expanding detail on a small screen may hit the screen cap. Acceptable; scrollbar appears.
- **Multi-row mapping**: ISO/ISEER 2-point has two rows (ISO, ISEER). Detail pane should map to the selected/comparison row, or show both. Design decision in 192-c: show a single combined detail table for all rows, or a row selector.
- **SASO optional 35 Min**: detail pane must handle the optional point gracefully (show "-" when disabled).
- **Testability**: detail table is read-only; tests verify row count and cell text for known inputs.

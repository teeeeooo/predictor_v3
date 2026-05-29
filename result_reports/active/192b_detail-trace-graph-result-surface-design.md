# 192-b Detail / Trace / Graph Result Surface Design

## Audit Scope

- Current section-local result tables (`IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`).
- `iso16358_tab.py` preferred-size and geometry reset behavior.
- UI/UX SSOT (`01_TOOLKIT_SELECTION_POLICY.md`, `02_DESIGN_TOKENS_AND_LAYOUT.md`, `03_SPREADSHEET_TABLE_UX_CONTRACT.md`).
- Core result shape (summary dict only; no bin/trace data exposed).

## Current Result Data

- Available: `measured` per-point `capacity`/`power`, result `cspf`/`cstl`/`csec` aliases.
- Missing: bin weights, intermediate calculation steps, seasonal breakdown.

## Surface Candidate Comparison

| Surface | User value | Core change | Impl size | Verdict |
| --- | --- | --- | --- | --- |
| Detail table | High | None | Small | **First slice** |
| Graph | Medium-high | None for point plots; needs bin data for seasonal | Medium | Second slice |
| Trace | Medium | Required (new data contract) | Medium-large | Deferred |

## Placement Comparison

| Placement | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| A. Section-local collapsible pane | Natural flow; ScrollableFrame absorbs overflow; no new window | Geometry impact when expanded | **Recommended** |
| B. Section-local tabs | Organized | ttk.Notebook complexity; overkill | Rejected |
| C. Separate Toplevel dialog | Zero geometry impact | Breaks flow; row mapping awkward | Rejected |
| D. App-level shared window | Central | Violates section-local ownership | Rejected |

## Geometry Policy

- Default detail pane: **collapsed** (no geometry impact at startup).
- User-initiated expand: section packs detail frame; call `_fit_toplevel_to_current_content` once.
- Preferred-size owner: `iso16358_tab` unchanged. Section natural size includes packed detail.
- No continuous `<Configure>` observer. No hardcoded pixel sizes.

## Graph Tooling

- Tkinter app stays on Tkinter.
- Matplotlib (`FigureCanvasTkAgg`) is acceptable per toolkit policy, but **not in the first slice**.
- Graph implementation deferred to a dedicated post-detail slice.

## Final Recommendation

- **Next implementation slice**: `192-c section-local detail table MVP`
  - Collapsible detail pane in `IsoIseer2PointSection` and `IsoSasoT3Section`.
  - Content: per-point capacity, power, EER/COP, plus annual energy summary.
  - Data from existing `measured`/`result` dicts (no core change).
  - Default collapsed; user expands; one-shot fit.

## Deferred

- Graph: after detail MVP is stable.
- Trace: after core exposes trace data contract.
- Multi/batch, EN/AHRI: unchanged.

## Excluded Scope

- Core/config/golden/profile registry changes.
- Hong Kong `ResultPanel` changes.
- Shared framework.
- Graph code in first slice.

## Verification

- Source/test modified: **none**.
- `python3 -B tools/check_code_structure.py`: OK.
- `git diff --check`: clean.

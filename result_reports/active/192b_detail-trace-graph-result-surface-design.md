# 192-b Detail / Trace / Graph Result Surface Design

## Audit Scope

- Current section-local result tables (`IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`).
- `iso16358_tab.py` preferred-size and geometry reset behavior.
- UI/UX SSOT (`01_TOOLKIT_SELECTION_POLICY.md`, `02_DESIGN_TOKENS_AND_LAYOUT.md`, `03_SPREADSHEET_TABLE_UX_CONTRACT.md`, `adapters/TKINTER_TABLE_ADAPTER.md`).
- Core result shape around `calculate_cspf()` / `calculate_hspf()` result data.
- PyQt reference trace/graph widgets (`TraceTableModel`, `BinGraphWidget`, `TraceDetailPanel`) and their `bin_details` flow.

## Current Result Data

- Available during Tk section calculation: `measured` per-point `capacity`/`power`, result `cspf`/`cstl`/`csec` aliases, and CSPF `result["bin_details"]`.
- Current rendered Tk tables retain only formatted rows/status; raw `measured`/`result` snapshots are not retained yet.
- PyQt reference trace/graph is bin-details based. This is distinct from an internal formula trace.
- Missing/stable-contract gap: normalized section-local snapshots and an internal formula trace contract.

## Surface Candidate Comparison

| Surface | User value | Core change | Impl size | Verdict |
| --- | --- | --- | --- | --- |
| Detail table | High | None; needs section-local snapshots | Small | **First slice** |
| Bin-details reference trace | Medium | None for CSPF raw result; needs snapshot retention | Medium | Later |
| Internal formula trace | Medium | Required stable core/data contract | Medium-large | Deferred |
| Graph | Medium-high | None for point/bin CSPF graphs; tooling/geometry unresolved | Medium | Later design |

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
- Compared: embedded matplotlib canvas, generated image displayed in Tk, separate image/export dialog, and deferring graph.
- No graph library or dependency is chosen in this design.
- Graph implementation is deferred to a dedicated post-detail slice.

## Final Recommendation

- **Next implementation slice**: `192-c section-local detail table MVP`
  - Collapsible detail pane in `IsoIseer2PointSection` and `IsoSasoT3Section`.
  - Content: per-point capacity, power, EER/COP, plus annual energy summary.
  - Data from retained section-local snapshots of existing `measured`/`result` dicts (no core change).
  - Default collapsed; user expands; one-shot fit.

## Deferred

- Graph: after detail MVP is stable.
- Bin-details reference trace: after detail MVP proves snapshot/placement.
- Internal formula trace: after core exposes a stable trace data contract.
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

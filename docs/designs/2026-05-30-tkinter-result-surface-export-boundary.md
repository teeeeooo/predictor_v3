# Tkinter Result Surface / Export Boundary

## Background

The Tkinter ISO profile sections now cover:

- ISO / ISEER 2-point comparison table.
- SASO T3 required-only vs optional-min comparison table.
- ISO / ISEER and SASO `bin_details` trace tables.
- Hong Kong CSPF/HSPF through the existing `ResultPanel` path.

The next likely slice is table CSV export. Before adding export buttons and later graph/export surfaces, the boundary should stay small enough to prevent section scripts from growing into mixed input, calculation, display, export, and graph modules.

## Current Surfaces

- `IsoIseer2PointSection` owns profile-specific input, dual-profile calculation orchestration, trace retention, and trace selector wiring.
- `IsoSasoT3Section` owns SASO input, optional 35 Min toggle, required/optional calculation orchestration, trace retention, and trace selector wiring.
- `IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`, and `BinTraceTable` own table display, formatting, status text, copy text, and table row exposure.
- `Iso16358Tab` owns profile switching, scroll reset, and one-shot fit after trace expand/collapse.

## Current Section Growth Risk

`IsoSasoT3Section` already combines input table setup, optional test state, calculator calls, result table updates, trace state, and trace UI wiring. Adding CSV export, graph rendering, graph export, and file dialog handling directly to each section would make the sections harder to keep narrow and harder to test.

## Boundary Decision

Keep the calculation sections profile-specific. Split only repeated result surface and export actions when they are needed.

- Section owns profile-specific input/calculation/state wiring.
- Reusable surface owns display/format/copy/export data hook.
- Export helper owns file writing and file dialog wrapper.
- Tab shell owns profile switch, scroll reset, and one-shot fit.

Do not introduce `BaseSection`, presenter/controller layers, or a shared result framework yet. The existing repeated pieces are still small enough for thin helper extraction rather than a broad UI framework change.

## What Stays Section-Local

- Input widgets and default values.
- Optional test toggles and validation state.
- Calculator/profile selection and measured input assembly.
- Scenario labels and profile-specific row selection.
- Trace selector state and unavailable-status decisions.
- Calls to the tab-owned one-shot fit callback.

## What Becomes Reusable Surface / Helper

- Table surfaces should expose a thin export data hook, preferably based on existing column labels and rendered rows.
- Copy behavior can remain on each table surface; export should reuse the same stable text/row data instead of re-reading calculator results.
- CSV file writing, save dialog handling, newline/encoding policy, and error wrapping belong in a small helper outside profile sections.

## What Not To Abstract Yet

- No `BaseSection`.
- No shared result framework.
- No presenter/controller layer.
- No forced migration of Hong Kong `ResultPanel`.
- No cross-profile raw result snapshot.

## CSV Export Implementation Boundary

The next implementation slice is `193-c table CSV export foundation`.

That slice should add:

- A small table export helper for CSV writing and save dialog wrapping.
- Thin hooks on table-shaped result/trace surfaces to provide exportable headers and rows.
- Minimal section wiring for export commands where the surface is visible and relevant.

It should not change calculator result schemas, profile routing, golden data, or table calculation behavior.

## Graph / HTML Export Boundary

Graph export should wait until graph parity exists. Later graph export may use a SPOT-style HTML export path when that is the simpler portable artifact. Do not add graph export before the graph surface and its data contract are defined.

## Hong Kong Trace Boundary

Hong Kong CSPF can likely use the existing `BinTraceTable` because its `bin_details` keys match the cooling trace schema.

Hong Kong HSPF must not be forced into the CSPF `BinTraceTable` schema. It needs a separate heating trace schema/table decision because its bin data is heating-specific.

## Next Implementation Slice

Proceed with `193-c table CSV export foundation` as a narrow export-helper and table-hook slice.

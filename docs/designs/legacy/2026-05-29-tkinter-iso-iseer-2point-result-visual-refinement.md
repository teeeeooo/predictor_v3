# Tkinter ISO/ISEER 2-point Result Visual Refinement Design

Date: 2026-05-29

This is a Design First Gate slice. It audits the existing PyQt reference and Tkinter implementation, compares result display options, and defines the next implementation slice. It does not implement UI code.

## Background

187-a/b/c added the Tkinter ISO tab `ISO / ISEER 2-point` profile and made it the default profile. The current result area renders two summaries, `ISO 16358-1` and `India ISEER`, through the shared `ResultPanel`. Manual smoke confirmed profile selection, table UX, scroll, and resize behavior.

The remaining issue is visual comparison. The stacked summaries are functionally correct, but users comparing ISO 16358-1 against India ISEER must scan two separate blocks.

## PyQt Reference Result Display

Relevant audit scope: `ui/calculators_2point.py`.

The PyQt reference has two result patterns:

- `TwoPointTableModel` includes per-input-row result columns: `EER Full`, `EER Half`, `ISO CSPF`, `India ISEER`, and `India CSEC [kWh]`.
- `IsoCspfSingleWidget` uses `RegionResultTableModel` for the primary single-calculation result table. For 2-point mode, rows are `ISO 16358-1` and `India ISEER`; columns are `Region/Profile`, `EER-Full`, `EER-Half`, `CSPF/SEER`, `CSTL [kWh]`, `CSEC [kWh]`.
- Detail/trace/graph is separate: `RegionDetailTab` owns summary text, graph mode selector, graph, and trace table. The primary result table is not the trace/detail surface.

Reference conclusion: the PyQt single 2-point result is a comparison table, not only two independent summaries. Detail/trace/graph must remain out of the primary result refinement slice.

## Current Tkinter Result Display

Relevant audit scope:

- `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/result_panel.py`
- `ui_tk/result_models.py`
- `ui_tk/sections/result_formatting.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `tests/test_ui_tk_profile_resolver.py`

Current `IsoIseer2PointSection` reads four numeric inputs, calculates each label from `two_point_profile_labels()`, and creates one `ResultSummary` per profile. `_summarize_two_point_result()` emits fields:

- `EER Full`
- `EER Half`
- `CSPF/ISEER`
- `CSTL [kWh]`
- `CSEC [kWh]`

`ResultPanel.set_summaries()` renders each summary as a compact table/card, one below the other, and keeps clipboard-compatible text via `ResultSummary.as_text()`.

Strengths:

- Reuses the existing result surface.
- Keeps invalid-input handling through status-only summaries.
- Preserves copy-text compatibility.
- Keeps Hong Kong CSPF/HSPF behavior unchanged because those sections already use the same `ResultPanel` contract.

Weaknesses:

- ISO and India values are not aligned in a single comparison grid.
- The repeated column headers increase visual height.
- `CSPF/ISEER` is correct as a shared field label, but it is less readable than a row-per-profile comparison.

## Candidate Comparison

### Candidate A: Keep Stacked `ResultSummary`, Refine Labels/Order

Pros:

- Smallest implementation change.
- Lowest risk to current tests.
- Reuses existing `ResultPanel` without new widget surface.

Cons:

- Does not solve the core comparison problem.
- Repeated headers remain.
- Visual result still differs from the PyQt single-result reference.

Impact:

- Likely limited to `ui_tk/sections/iso_iseer_2point_section.py` and tests.

Hong Kong conflict risk:

- Low, unless shared labels or `ResultPanel` behavior are changed.

Test scope:

- Update 2-point label/order assertions only.

Rollback cost:

- Very low.

### Candidate B: Add a 2-point-only Comparison Table Surface

Pros:

- Directly matches the PyQt primary result shape: profile rows and metric columns.
- Keeps `ResultPanel` unchanged for Hong Kong CSPF/HSPF.
- Keeps the implementation localized to the 2-point section and an optional small helper/model.
- Allows copy text to stay explicit and table-like.

Cons:

- Adds one small UI surface instead of reusing `ResultPanel` exactly.
- Needs focused tests for row labels, columns, invalid state, and Hong Kong non-impact.

Impact:

- Candidate files: `ui_tk/sections/iso_iseer_2point_section.py`; optional new helper in `ui_tk/sections/` or `ui_tk/`.
- No core calculator, resolver, profile selector, scroll, or geometry changes.

Hong Kong conflict risk:

- Very low if the surface is owned by `IsoIseer2PointSection` and `ResultPanel` is not modified.

Test scope:

- 2-point default render comparison rows/columns.
- Input change updates both rows without append growth.
- Invalid input renders safe status.
- Hong Kong CSPF/HSPF `ResultPanel` tests remain unchanged.

Rollback cost:

- Low. Revert the section-local surface and return to `ResultPanel.set_summaries()`.

### Candidate C: Add Comparison-Style Rendering Option to `ResultPanel`

Pros:

- Keeps one result component API.
- Could be reused by future comparison outputs.

Cons:

- Expands `ResultPanel` responsibility beyond compact metric summaries.
- Higher regression risk for Hong Kong CSPF/HSPF status-only and summary-table tests.
- Requires API/design decisions that are broader than the 2-point refinement.

Impact:

- `ui_tk/result_panel.py`, `ui_tk/result_models.py`, 2-point section, and multiple tests.

Hong Kong conflict risk:

- Medium. `ResultPanel` is already the owner for existing CSPF/HSPF surfaces.

Test scope:

- Existing Hong Kong result rendering, invalid status-only behavior, copy text, and 2-point comparison behavior.

Rollback cost:

- Medium because the shared component contract would change.

## Recommendation

Choose Candidate B: add a 2-point-only comparison table surface.

Reasoning:

- The user-facing problem is specifically 2-point profile comparison.
- The PyQt reference primary result is a comparison table, while detail/trace/graph is separate.
- `ResultPanel` is already stable for Hong Kong CSPF/HSPF; changing it for one comparison use case would broaden risk.
- A section-local surface can be implemented as a small 189-b slice and rolled back cleanly.

## 189-b Implementation Scope

Allowed scope for 189-b:

- Improve only the `ISO / ISEER 2-point` result display.
- Keep the current 2-point profile selector/input/default values/calculation behavior.
- Render rows for `ISO 16358-1` and `India ISEER`.
- Render columns: `Region/Profile`, `EER Full`, `EER Half`, `CSPF/ISEER`, `CSTL [kWh]`, `CSEC [kWh]`.
- Keep invalid input as a safe status surface or equivalent single safe status row.
- Preserve clipboard-compatible text without raw dicts, tracebacks, `None`, or long unformatted floats.
- Ensure Hong Kong CSPF/HSPF result display remains unchanged.

Candidate implementation files:

- `ui_tk/sections/iso_iseer_2point_section.py`
- Optional small helper/model if needed, for example `ui_tk/sections/iso_iseer_2point_result_table.py`

## Tests Proposal

Focused tests only:

- Update `tests/test_ui_tk_iso_table_autocalc.py` 2-point render assertions to check comparison rows/columns.
- Keep/update the input-change test to assert both profile rows update and no append growth occurs.
- Keep/update invalid input test to assert safe status and no raw exception output.
- Keep Hong Kong tests asserting existing `ResultPanel` summary behavior for CSPF/HSPF.
- Keep `tests/test_ui_tk_profile_resolver.py` unchanged unless labels change, which is not recommended.

## Excluded Scope

189-b must not include:

- SASO
- multi/batch
- detail/trace table
- graph
- core calculator changes
- golden/fixture changes
- PyQt retirement
- window geometry / scroll changes
- `ResultPanel` large redesign
- Hong Kong CSPF/HSPF result redesign

## Split Criteria

Keep 189-b as one implementation slice if the comparison surface is section-local and tests remain focused.

Split into 189-b/189-c if any of the following becomes necessary:

- A generic reusable comparison result model/API is introduced.
- `ResultPanel` must change.
- Copy/export behavior needs a shared table abstraction.
- Visual token/layout ownership changes beyond existing `ui_tk/layout_constants.py`.

## Risks / Open Questions

- The exact Tkinter widget shape should stay minimal: a bordered table-like frame is enough; a full Excel-like editable table is not needed for read-only results.
- Copy text should remain easy to inspect in existing tests, but exact TSV vs current pipe-separated text can be decided in 189-b if the UI surface owns it locally.
- If future SASO or multi/batch needs the same surface, generalization should be a later design slice, not part of 189-b.

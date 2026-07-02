# Tkinter ISO/ISEER 2-Point Single Calculation Design

## Background

Report 186 found that the Tkinter calculator now covers the Hong Kong
CSPF/HSPF shell, metric sub-tabs, auto-calc, summary panel,
Excel-like table behavior, and window geometry / scroll foundation.
The PyQt/reference calculator still has ISO16358 features that are not
yet migrated to Tkinter:

- ISO 16358-1 / India ISEER 2-point single calculation.
- SASO T3.
- ISO/ISEER multi/batch calculation.
- Detail / bin trace / graph surfaces.

The next implementation slice should start with ISO/ISEER 2-point
single calculation, not EN/AHRI expansion and not SASO/multi/detail.

## PyQt Reference 2-Point Flow

Relevant owner: `ui/calculators_2point.py`.

- `IsoCspfSingleWidget.PROFILE_TWO_POINT` is the user-facing mode.
- `TWO_POINT_REGIONS` contains:
  - `("iso", "ISO 16358-1")`
  - `("india", "India ISEER")`
- `TWO_POINT_INPUTS` contains:
  - `("35 Full", "35_full")`
  - `("35 Half", "35_half")`
- `_load_calculators()` maps:
  - `iso` -> `iso_t1_default_2point_cspf`
  - `india` -> `india_iseer_cspf`
- `_build_two_point_inputs()` installs a two-column capacity/power grid.
- `_recalculate_two_point()` reads measured 35 Full / 35 Half inputs,
  calls `calculate_cspf(measured)` for both calculators, and renders
  rows with:
  - `Region/Profile`
  - `EER-Full`
  - `EER-Half`
  - `CSPF/SEER`
  - `CSTL [kWh]`
  - `CSEC [kWh]`

Core profile/config evidence:

- `core/calculators/profiles.py` already enables
  `iso_t1_default_2point_cspf` and `india_iseer_cspf`.
- `data/region_configs/iso_t1_default_2point.json` and
  `data/region_configs/india_iseer.json` both use measured
  `35_full` / `35_half` plus derived 29 C points.

## Current Tkinter Structure

Relevant owners:

- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/profile_resolver.py`
- `ui_tk/sections/iso_cspf_section.py`
- `ui_tk/sections/iso_hspf_section.py`
- `ui_tk/metric_input_table.py`
- `ui_tk/excel_like_table_controller.py`
- `ui_tk/result_panel.py`

Current shape:

- `Iso16358Tab` owns a top-level region selector and a metric notebook.
- `profile_resolver.py` currently exposes only `Hong Kong`.
- Hong Kong renders two metric sub-tabs: `CSPF` and `HSPF`.
- `IsoCspfSection` and `IsoHspfSection` own their input tables,
  auto-calc, profile resolution, calculator calls, and result panels.
- `MetricInputTable` and `ExcelLikeTableController` already provide the
  needed bordered matrix and Excel-like interactions.
- `ResultPanel` can render multiple `ResultSummary` objects, but it
  currently renders them as compact stacked summary cards rather than a
  PyQt-style comparison table.

Main structural problem: the current ISO tab is Hong Kong-centered.
Adding ISO/ISEER 2-point inside that shape without an explicit mode
boundary would make the Hong Kong skeleton look like the whole ISO tab.

## UI Placement Options

| Option | Shape | Pros | Cons / risks |
| --- | --- | --- | --- |
| A. Extend existing region selector | Add labels such as `ISO / ISEER 2-point` to the current region selector. | Smallest visible change. Reuses current `_render_region()` path. | Misuses "region": ISO/ISEER 2-point is a comparison mode, not one region. Makes India ISEER and ISO T1 look like one region. Hard to add SASO later without semantic drift. |
| B. Add top-level profile/mode selector | ISO tab gets a mode selector above the current content. `Hong Kong` mode keeps region selector + CSPF/HSPF metric tabs. `ISO/ISEER 2-point` mode renders a separate 2-point section. | Separates global/reference mode from Hong Kong region behavior. Preserves existing Hong Kong CSPF/HSPF tabs. Provides a clean future slot for SASO without pretending it is a Hong Kong metric. | Requires a small render branch in `Iso16358Tab` and a new mode resolver/registry. |
| C. Add profile selector inside CSPF metric tab | Keep Hong Kong metric notebook and add a sub-selector inside CSPF for Hong Kong vs ISO/ISEER 2-point. | Avoids a new top-level selector. Keeps "cooling" under CSPF. | Conflates Hong Kong CSPF with generic ISO/ISEER comparison. Leaves HSPF sibling visible while the CSPF tab is no longer Hong Kong-specific. Harder to explain and test. |

## Decision

Use **Option B: add a top-level profile/mode selector**.

Recommended user-facing modes:

- `Hong Kong`
- `ISO / ISEER 2-point`

Behavior:

- `Hong Kong` keeps the current region selector, metric sub-tabs, and
  existing CSPF/HSPF sections unchanged.
- `ISO / ISEER 2-point` renders a new section that is independent of
  Hong Kong CSPF/HSPF sections.
- The implementation must not expose `profile_id`, `calculator_id`, or
  config paths in the UI.
- The first 2-point implementation should not include SASO, multi,
  detail table, or graph.

## Input Shape

Create a new Tkinter section for ISO/ISEER 2-point single calculation.
Suggested name: `IsoIseer2PointSection`.

Input table:

- Reuse `MetricInputTable`.
- Columns:
  - `("full", "35 Full")`
  - `("half", "35 Half")`
- Rows:
  - `("capacity", "능력 [W]")`
  - `("power", "전력 [W]")`
- Editable fields:
  - `full_capacity`
  - `full_power`
  - `half_capacity`
  - `half_power`

Default sample values:

- Use sample defaults in the first implementation unless this creates
  unacceptable test brittleness:
  - full capacity `3600`
  - full power `900`
  - half capacity `1700`
  - half power `380`
- Reason: the current Tkinter calculator uses immediate render with
  smoke values, and a default populated section makes the new mode easy
  to smoke without manual setup.

## Result Shape

The result should preserve the PyQt/reference columns:

- `EER Full`
- `EER Half`
- `CSPF/ISEER`
- `CSTL [kWh]`
- `CSEC [kWh]`

The two result rows are:

- `ISO 16358-1`
- `India ISEER`

Implementation recommendation for 187-b:

- Use existing `ResultPanel.set_summaries()` with two `ResultSummary`
  objects, one titled `ISO 16358-1` and one titled `India ISEER`.
- Include the fields above in each summary.
- Treat this as "side-by-side" at the data level: both profiles are
  calculated from the same input and rendered together in one result
  panel. If a literal horizontal comparison table is required later,
  split it into a visual refinement slice after the calculation path is
  stable.

## Implementation Slice Proposal

187-b should be scoped to ISO/ISEER 2-point single calculation only.

Candidate source files for 187-b:

- New `ui_tk/sections/iso_iseer_2point_section.py`
  - owns input table, controllers, auto-calc, two calculator calls, and
    local result rendering.
- `ui_tk/tabs/iso16358_tab.py`
  - adds the top-level mode selector and render branch.
  - keeps existing Hong Kong mode behavior as the default.
- `ui_tk/profile_resolver.py`
  - adds a small public resolver or registry for the 2-point profile
    display labels to `profile_id` mapping.
  - does not expose raw ids in UI.
- `ui_tk/sections/result_formatting.py`
  - adds a helper for 2-point cooling summaries if keeping formatting
    outside the section stays simpler.

Avoid touching:

- `core/calculators/profiles.py`
- `data/region_configs/*.json`
- calculator core
- golden fixtures
- PyQt source

## Tests Proposal

Focused tests for 187-b:

- `tests/test_ui_tk_profile_resolver.py`
  - resolver exposes ISO/ISEER 2-point profile ids through UI-safe names.
  - Hong Kong CSPF/HSPF resolver behavior remains unchanged.
- `tests/test_ui_tk_iso_table_autocalc.py`
  - ISO tab defaults to Hong Kong mode and still renders CSPF/HSPF tabs.
  - selecting `ISO / ISEER 2-point` renders the new section.
  - default 2-point values render two summaries: `ISO 16358-1` and
    `India ISEER`.
  - editing one input updates both summaries.
  - invalid input shows status-only error without traceback/raw dict.
- Existing table-controller focused tests remain the owner for copy,
  paste, clear, undo, and navigation behavior.
- Existing geometry/scroll focused tests remain the owner for shell
  behavior.

Verification for 187-b:

- `python3 -B tools/check_code_structure.py`
- `python3 -B -m py_compile` for changed source and focused tests.
- Focused pytest only for changed UI resolver/section tests.
- No full pytest unless a later implementation prompt explicitly
  widens verification.

## Split Criteria

Keep 187-b as one implementation slice if:

- the new section stays near the current section size;
- `ResultPanel` can render two profile summaries without a new result
  widget;
- `Iso16358Tab` changes are a small render branch, not a root layout
  rewrite.

Split into 187-b / 187-c if:

- a new reusable comparison-table result widget is required;
- the mode selector introduces broad navigation refactoring;
- resolver changes start mixing region, metric, profile, and mode
  concepts in one mapping;
- the new section exceeds the existing soft size limits or needs more
  than one new responsibility.

Suggested split if needed:

- 187-b: mode selector + 2-point section + stacked summaries.
- 187-c: comparison-table visual refinement or generic profile-mode
  registry cleanup.

## Excluded Scope

Do not include in 187-b:

- SASO T3.
- SASO required/minimum toggle.
- ISO/ISEER multi/batch calculation.
- Detail panel.
- Bin trace table.
- Graph / load-capacity graph.
- EN/AHRI extension.
- PyQt retirement.
- Core calculator/profile/config/golden/fixture changes.

## Risks / Open Questions

- Result presentation: stacked `ResultSummary` cards are lower risk than
  a new comparison table, but they may not visually match PyQt's row
  table. Treat literal horizontal comparison as a later refinement unless
  the user requires it for 187-b.
- Mode naming: `ISO / ISEER 2-point` is accurate but long. Keep it for
  clarity unless UI width becomes a real issue.
- Resolver boundary: avoid making `(region, metric)` resolver carry
  global comparison modes. A small profile-mode resolver or registry may
  be cleaner.
- Default sample values should be tested as smoke values, not as new
  golden references.

# Design Gate Summary

## Goal

Prepare a safe implementation boundary for adding ISO 16358-1 / India
ISEER 2-point single calculation to the Tkinter calculator.

## Confirmed Decisions

- Use a top-level profile/mode selector in `Iso16358Tab`.
- Keep Hong Kong as the default mode.
- Keep the existing Hong Kong region selector and CSPF/HSPF metric
  sub-tabs unchanged in Hong Kong mode.
- Add ISO/ISEER 2-point as a separate section, not as extra logic inside
  `IsoCspfSection`.
- Reuse `MetricInputTable`, `ExcelLikeTableController`,
  `DebouncedAutoCalc`, and `ResultPanel`.
- Render ISO 16358-1 and India ISEER together from the same input.

## Core vs Handler Boundary

- Core calculators and region configs remain unchanged.
- Tkinter UI owns mode selection, input collection, display formatting,
  and user-facing profile labels.
- Profile id mapping remains hidden behind a Tkinter-side resolver or
  registry.
- Country/region behavior stays in profile/config/calculator routing;
  the UI does not mutate global ISO behavior.

## Data Shape / API Boundary

Input to core:

```python
{
    "35_full": {"capacity": full_capacity, "power": full_power},
    "35_half": {"capacity": half_capacity, "power": half_power},
}
```

Calculator calls:

```python
create_calculator_for_profile("iso_t1_default_2point_cspf").calculate_cspf(measured)
create_calculator_for_profile("india_iseer_cspf").calculate_cspf(measured)
```

User-facing result fields:

- `EER Full`
- `EER Half`
- `CSPF/ISEER`
- `CSTL [kWh]`
- `CSEC [kWh]`

## Required Tests

- Hong Kong mode remains default and unchanged.
- ISO/ISEER 2-point mode renders a new section.
- Default 2-point values render ISO 16358-1 and India ISEER summaries.
- Editing one input updates both summaries.
- Invalid numeric input renders a status-only error.
- Existing Excel-like table controller tests remain the interaction
  contract owner.

## Migration / Refactor Path

1. Add a UI-safe 2-point profile mapping.
2. Add `IsoIseer2PointSection`.
3. Add a small mode selector/render branch in `Iso16358Tab`.
4. Add focused tests.
5. Defer SASO, multi, detail, and graph until the single 2-point path is
   stable.

## Risks

- Overloading the existing region selector would blur region vs profile
  mode semantics.
- Putting 2-point under the CSPF metric tab would make Hong Kong and
  generic ISO/ISEER behavior too tightly coupled.
- A new comparison table may inflate the first implementation slice.

## Non-goals

- SASO T3.
- Multi/batch.
- Detail / trace / graph.
- EN/AHRI.
- PyQt retirement.
- Core calculator/config/golden changes.

## Next Codex Implementation Prompt

Implement `187-b ISO/ISEER 2-point single calculation` as a focused
Tkinter UI slice: add a profile/mode selector to `Iso16358Tab`, create
an `IsoIseer2PointSection` that reuses `MetricInputTable` and
`ResultPanel`, resolve `iso_t1_default_2point_cspf` and
`india_iseer_cspf` through a UI-safe resolver, add focused tests, and do
not implement SASO, multi, detail, graph, EN/AHRI, or core/config
changes.

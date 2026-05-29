# Tkinter SASO T3 Profile Design

Date: 2026-05-30

This is a Design First Gate slice. It audits the existing PyQt/reference SASO T3 path and defines a small Tkinter implementation slice. No source or tests are changed by this design.

## Background

Tkinter currently supports `ISO / ISEER 2-point` and `Hong Kong` under the ISO profile selector. PyQt/reference still includes `SASO T3` as a calculator profile. The next feature candidate is adding SASO T3 to Tkinter without implementing multi/batch, detail/trace, or graph surfaces.

## Reference Audit Summary

Relevant evidence:

- `core/calculator_profiles.py` already has `profile_id="saso_t3_cspf"` using `calculator_id="iso16358"` and `data/region_configs/saso.json`.
- `data/region_configs/saso.json` is a SASO / ISO 16358-1 T3 cooling profile with `reference_point="46_full"`, `t_100_load=46.0`, and default `cspf_test_profile.test_selection="with_optional_test"`.
- `ui/calculators_2point.py` `IsoCspfSingleWidget` exposes `PROFILE_SASO_T3 = "SASO T3"`.
- PyQt required inputs are `46 Full`, `35 Full`, `35 Half`; optional input adds `35 Min` via a `35°C Minimum 사용` checkbox.
- PyQt result is a single row, not a two-profile comparison: `Region/Profile`, `EER 46-Full`, `EER 35-Full`, `EER 35-Half`, `EER 35-Min`, `CSPF`, `CSTL [kWh]`, `CSEC [kWh]`.
- When optional min is off, PyQt creates the calculator and overrides `calculator.config["cspf_test_profile"]["test_selection"] = "required_only"`.
- PyQt detail/graph/trace exists through `RegionDetailTab`, but that is separate from the primary result and stays out of scope.

## Current Tkinter Structure

- `ui_tk/profile_resolver.py` currently lists only `ISO / ISEER 2-point` and `Hong Kong`.
- `ui_tk/tabs/iso16358_tab.py` switches between a 2-point section and Hong Kong metric sub-tabs.
- `IsoIseer2PointSection` is specific to ISO/India two-profile comparison.
- `IsoIseer2PointResultTable` is specific to row comparison across profiles.
- Hong Kong CSPF/HSPF uses per-metric sections and `ResultPanel` summary cards.

## Input Shape Proposal

Add a SASO-specific section with:

- Required columns: `46 Full`, `35 Full`, `35 Half`
- Optional column: `35 Min`
- Rows: `능력 [W]`, `전력 [W]`
- A checkbox/toggle for optional `35 Min`

Do not reuse editable result tables or comparison-table widgets as input surfaces. Use the existing `MetricInputTable` + `ExcelLikeTableController` pattern.

## Profile Selector Placement

Add `SASO T3` as a third `ISO 프로파일` selector option:

1. `ISO / ISEER 2-point`
2. `Hong Kong`
3. `SASO T3`

`Iso16358Tab` should render a section-local SASO frame for the SASO mode. It should not expose a duplicate region selector.

## Result Display Proposal

Use a SASO section-local single-result summary, not the 2-point comparison table.

Suggested fields:

- `EER 46 Full`
- `EER 35 Full`
- `EER 35 Half`
- `EER 35 Min` only when optional min is enabled, or displayed as `-`
- `CSPF`
- `CSTL [kWh]`
- `CSEC [kWh]`

`ResultPanel` can be reused for a single `ResultSummary` if the field count remains readable. If width becomes poor, add a SASO-only read-only table surface in the implementation slice rather than changing shared `ResultPanel`.

## Candidate Comparison

### Candidate A: Add `SASO T3` Selector Mode and Dedicated SASO Section

Pros:

- Matches the distinct SASO input shape.
- Keeps ISO/ISEER 2-point and Hong Kong sections unchanged.
- Small implementation slice: resolver label, one section, focused tests.
- Low rollback cost.

Cons:

- Some formatting/calculation helper duplication with 2-point section may appear.
- Optional min toggle needs careful stale-value/status handling.

Impact:

- `ui_tk/profile_resolver.py`, `ui_tk/tabs/iso16358_tab.py`, new SASO section, focused tests.

Regression risk:

- Low if existing modes are left intact and tests assert mode switching.

### Candidate B: Extend `IsoIseer2PointSection` to Include SASO

Pros:

- Fewer new files.
- Can reuse some EER/formatting helpers directly.

Cons:

- Conflates two-profile comparison with single SASO profile.
- Increases risk to the working ISO/ISEER 2-point default.
- Optional `35 Min` makes the section more conditional and harder to reason about.

Impact:

- Existing 2-point section and tests would need broader changes.

Regression risk:

- Medium for 2-point default/result table.

### Candidate C: Extract a Common 2-point/SASO Base Helper First

Pros:

- Could reduce future duplication for repeated capacity/power point tables.
- May help later EN/AHRI/profile extensions.

Cons:

- Larger design/implementation slice.
- Refactor risk before adding a single feature.
- Delays user-visible SASO support.

Impact:

- New shared helper/model plus section rewiring.

Regression risk:

- Medium to high unless split into a separate boundary design and implementation.

## Recommendation

Choose Candidate A: add `SASO T3` to the profile selector with a dedicated SASO section.

Reasoning:

- SASO has a distinct input shape and optional min toggle.
- The primary result is a single profile row/summary, not a comparison across profiles.
- A dedicated section keeps the next implementation small and minimizes risk to Hong Kong and ISO/ISEER 2-point.

## Implementation Slice Scope

Suggested next slice: `190-b SASO T3 implementation slice`.

Include:

- Add SASO label/profile resolver path.
- Add `IsoSasoT3Section` or similarly named section.
- Use `MetricInputTable` + `ExcelLikeTableController`.
- Add optional `35 Min` toggle.
- Call `create_calculator_for_profile(profile_id="saso_t3_cspf")`.
- If optional min is off, set `cspf_test_profile.test_selection` to `required_only` on the calculator instance.
- Render safe status for incomplete/invalid input.
- Preserve profile-switch exact-fit and preferred size behavior.

## Tests Proposal

- Resolver includes `SASO T3` in calculation mode labels.
- SASO mode renders required input columns and optional-min toggle.
- Optional min toggle adds/removes or enables/disables `35 Min` input.
- Default SASO calculation renders safe summary without raw dicts, tracebacks, `None`, or long floats.
- Invalid input clears stale success values and shows safe status.
- Switching among ISO/ISEER 2-point, Hong Kong, and SASO preserves existing modes.
- Focused app smoke keeps PyQt unimported and profile-switch exact-fit stable.

## Excluded Scope

- SASO multi/batch
- detail/trace table
- graph
- EN/AHRI
- core calculator changes
- profile/config/golden/fixture changes
- PyQt source changes
- generic shared section framework

## Risks / Open Questions

- `ResultPanel` may be too wide if all SASO fields are shown in one compact row; implementation can keep it simple first and only introduce a SASO-local result table if needed.
- Optional `35 Min` UX should avoid stale hidden values.
- Future tabs/profiles can reuse the profile-switch exact-fit hook, but each tab/profile must own accurate preferred size calculation. Hidden tabs, graph/detail, and dynamic result surfaces need preferred-size ownership in their own design slices.

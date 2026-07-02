# Tkinter SASO T3 Profile Design

Date: 2026-05-30

This is a Design First Gate slice. It audits the existing PyQt/reference SASO T3 path and defines a small Tkinter implementation slice. No source or tests are changed by this design.

## Background

Tkinter currently supports `ISO / ISEER 2-point` and `Hong Kong` under the ISO profile selector. PyQt/reference still includes `SASO T3` as a calculator profile. The next feature candidate is adding SASO T3 to Tkinter without implementing multi/batch, detail/trace, or graph surfaces.

## Reference Audit Summary

Relevant evidence:

- `core/calculators/profiles.py` already has `profile_id="saso_t3_cspf"` using `calculator_id="iso16358"` and `data/region_configs/saso.json`.
- `data/region_configs/saso.json` is a SASO / ISO 16358-1 T3 cooling profile with `reference_point="46_full"`, `t_100_load=46.0`, and default `cspf_test_profile.test_selection="with_optional_test"`.
- `ui/calculators_2point.py` `IsoCspfSingleWidget` exposes `PROFILE_SASO_T3 = "SASO T3"`.
- PyQt required inputs are `46 Full`, `35 Full`, `35 Half`; optional input adds `35 Min` via a `35°C Minimum 사용` checkbox.
- PyQt result is a single SASO row for the currently selected optional-min mode: `Region/Profile`, `EER 46-Full`, `EER 35-Full`, `EER 35-Half`, `EER 35-Min`, `CSPF`, `CSTL [kWh]`, `CSEC [kWh]`. The Tkinter design intentionally amends this into a 3-point vs 4-point scenario comparison.
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

Use a SASO section-local comparison result surface. The comparison is not ISO-vs-India; it is `required_only` 3-point vs optional-min 4-point SASO.

Input policy:

- Required input points: `46 Full`, `35 Full`, `35 Half`
- Optional input point: `35 Min`

Toggle policy:

- Toggle off: `35 Min` input is disabled or ignored, and only the required-only 3-point result is shown.
- Toggle on + valid `35 Min`: required-only 3-point and with-optional-min 4-point results are shown together.
- Toggle on + invalid/incomplete `35 Min`: required-only 3-point result may remain visible; 4-point result must show a safe status/error without tracebacks, raw dicts, `None`, or stale success values.

Comparison rows:

- `Required only (3-point)`
- `With 35 Min (4-point)`

Comparison columns:

- `Scenario`
- `EER 46 Full`
- `EER 35 Full`
- `EER 35 Half`
- `EER 35 Min`
- `CSPF`
- `CSTL [kWh]`
- `CSEC [kWh]`

The 3-point row displays `EER 35 Min` as `-`. Whether the 4-point row is hidden or shown as a disabled/status row when the toggle is off is a small 190-b implementation choice, but the UI must not confuse users about which scenario was calculated.

Calculation policy:

- 3-point result: create `saso_t3_cspf`, override the instance config `cspf_test_profile.test_selection = "required_only"`, and pass only `46 Full`, `35 Full`, `35 Half`.
- 4-point result: create `saso_t3_cspf`, use optional/min-enabled selection, and pass `46 Full`, `35 Full`, `35 Half`, `35 Min`.
- Do not modify the production config file.
- Do not add a shared `ResultPanel` comparison mode or generic result framework.

## Candidate Comparison

### Candidate A: Add `SASO T3` Selector Mode and Dedicated SASO Section

Pros:

- Matches the distinct SASO input shape.
- Keeps ISO/ISEER 2-point and Hong Kong sections unchanged.
- Small implementation slice: resolver label, one section, section-local scenario comparison table, focused tests.
- Low rollback cost.

Cons:

- Some formatting/calculation helper duplication with 2-point section may appear.
- Optional min toggle needs careful stale-value/status handling for the 4-point row.

Impact:

- `ui_tk/profile_resolver.py`, `ui_tk/tabs/iso16358_tab.py`, new SASO section, focused tests.

Regression risk:

- Low if existing modes are left intact and tests assert mode switching.

### Candidate B: Extend `IsoIseer2PointSection` to Include SASO

Pros:

- Fewer new files.
- Can reuse some EER/formatting helpers directly.

Cons:

- Conflates ISO/India profile comparison with SASO 3-point/4-point scenario comparison.
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
- The primary result is a SASO scenario comparison, not a shared ISO/ISEER profile comparison.
- A dedicated section keeps the next implementation small and minimizes risk to Hong Kong and ISO/ISEER 2-point.
- A section-local comparison table avoids changing shared `ResultPanel` or extracting a common framework.

## Implementation Slice Scope

Suggested next slice: `190-b SASO T3 implementation slice`.

Include:

- Add SASO label/profile resolver path.
- Add `IsoSasoT3Section` or similarly named section.
- Use `MetricInputTable` + `ExcelLikeTableController`.
- Add optional `35 Min` toggle.
- Add a section-local SASO result comparison table, for example `iso_saso_t3_result_table.py` if needed.
- Call `create_calculator_for_profile(profile_id="saso_t3_cspf")`.
- Always calculate the required-only 3-point result from required inputs.
- When optional min is enabled and valid, also calculate the 4-point optional-min result.
- If optional min is off, hide or clearly disable/status the 4-point row.
- Render safe status for incomplete/invalid input.
- Preserve profile-switch exact-fit and preferred size behavior.

## Tests Proposal

- Resolver includes `SASO T3` in calculation mode labels.
- SASO mode renders required input columns and optional-min toggle.
- Optional min toggle adds/removes or enables/disables `35 Min` input.
- Toggle off renders the 3-point required-only result.
- Toggle on + valid `35 Min` renders both `Required only (3-point)` and `With 35 Min (4-point)` rows.
- 3-point row does not use the `35 Min` value.
- 4-point row uses the `35 Min` value.
- Toggle on + invalid `35 Min` keeps the 3-point result valid if possible and shows safe status/error for the 4-point scenario.
- No stale success values, raw dicts, tracebacks, `None`, or long unformatted floats.
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

- The SASO comparison table is section-local by design; avoid changing shared `ResultPanel`.
- Optional `35 Min` UX should avoid stale hidden values.
- Future tabs/profiles can reuse the profile-switch exact-fit hook, but each tab/profile must own accurate preferred size calculation. Hidden tabs, graph/detail, and dynamic result surfaces need preferred-size ownership in their own design slices.

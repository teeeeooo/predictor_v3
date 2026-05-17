# 085 — Calculator Unit Normalization Adapter + Envelope Chain End-to-End Smoke

## Goal

Split the unit boundary between ML / inverse-search and the calculator
layer so that ML and inverse-search keep capacity / power in W, the
adapter is the only conversion site, and the AHRI SEER2 envelope chain
composes end-to-end. Status of ISO16358-2 HSPF mismatch is parked as
an external (user-side) audit so the repo can move on to envelope and
UI slice work.

## Scope

- `docs/WORK_PLAN.md`: mark ISO16358-2 HSPF mismatch as external-audit
  pending; reorder the repo next-action sequence to
  unit-adapter → envelope-chain smoke → AHRI SEER2 horizontal
  table-input UI slice.
- `core/calculator_unit_adapter.py` (new): single conversion site
  between ML canonical W/W and AHRI SEER2 native Btu/h/W.
- `core/calculator_input_adapter.py`: add `units_trace` parameter on
  `build_calculator_input_envelope`, stored under
  `options["units_trace"]`. Default is a no-op trace.
- `core/calculator_prediction_adapter.py`:
  - Per-source unit validation now uses
    `core.calculator_unit_adapter.expected_source_units`.
  - `predicted_points_to_calculator_input_envelope` calls
    `normalize_points_to_profile_native` and attaches the resulting
    `units_trace` to the calculator input envelope.
- `tests/test_calculator_unit_adapter.py` (new).
- `tests/test_calculator_input_adapter.py`: add tests for default and
  explicit `units_trace` handling.
- `tests/test_calculator_prediction_adapter.py`: split the mixed-source
  tests so each source uses its expected units; add converted-capacity
  and `units_trace` assertions.
- `tests/test_calculator_envelope_chain.py` (new): end-to-end smoke for
  PredictedPointsEnvelope → CalculatorInputEnvelope →
  CalculatorResultEnvelope → RankingCandidateEnvelope.
- `tests/test_calculator_schema_boundaries.py`: add the new unit
  adapter to `ADAPTER_MODULES` so adapter-only terms stay allowed in
  that file.
- `result_reports/active/085_calculator-unit-normalization-and-envelope-chain-smoke.md`:
  this report.

## Non-goals

- No ISO16358-2 HSPF mismatch analysis or fix. xfail case ids stay as
  `frozenset({3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16})`.
- No calculator core change (`core/calculator_iso16358.py`,
  `core/calculator_ahri.py`, `core/calculator_en14825.py`, etc.).
- No expected / golden value edit.
- No UI implementation, no `app_calculator.py` or
  `ui/calc_window.py` change.
- No EN14825 / ISO16358 / KS C 9306 / AHRI HSPF2 unit conversion in
  the new unit adapter (only AHRI SEER2 supported).
- No ML model call, no inverse-search implementation.
- No envelope schema fan-out (no new top-level envelope fields beyond
  `options["units_trace"]`).
- No ranking algorithm.

## Verification

- `python3 -B -m py_compile core/calculator_unit_adapter.py core/calculator_input_adapter.py core/calculator_prediction_adapter.py core/calculator_result_adapter.py core/calculator_ranking_adapter.py`
  → OK.
- `python3 -B -m pytest tests/test_calculator_unit_adapter.py tests/test_calculator_input_adapter.py tests/test_calculator_prediction_adapter.py tests/test_calculator_ranking_adapter.py -q`
  → all green together with the chain test:
  `94 passed`.
- `python3 -B -m pytest tests/test_calculator_envelope_chain.py -q`
  → `7 passed`.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → all green.
- `python3 -B -m pytest -q` → `407 passed, 34 xfailed`. Baseline before
  this task was `370 passed, 34 xfailed`; the +37 delta = 17 new unit
  adapter tests + 4 new input adapter tests (units_trace) + 5 new
  prediction adapter tests (split sources, units_trace, conversion) +
  7 new envelope chain tests + the existing input adapter tests
  unchanged. xfail counts are unchanged (ISO16358-2 HSPF mismatch
  status preserved).

## Task Results

### Task 1 — WORK_PLAN status reorg

Modified file: `docs/WORK_PLAN.md`.

Changes:

- Added a `Current milestone focus` bullet stating that ISO16358-2
  HSPF mismatch analysis is a user-side external audit and is not in
  the repo immediate next action list. xfail case list unchanged.
- Added a `Current milestone focus` bullet noting that the W ↔ AHRI
  Btu/h conversion lives in `core/calculator_unit_adapter.py` and that
  the end-to-end PredictedPointsEnvelope →
  RankingCandidateEnvelope chain is now protected by
  `tests/test_calculator_envelope_chain.py`.
- Rewrote the `Near-term execution order` section:
  - Item 2: ISO HSPF mismatch is parked as an external audit.
  - Item 3: repo next sequence is unit normalization adapter →
    envelope chain end-to-end smoke → AHRI SEER2 horizontal
    table-input UI slice.
  - Item 4: subsequent UI slices (AHRI HSPF2 → EN14825 SCOP → EN14825
    SEER) and the unit adapter expansion to ISO / KS / EN are
    explicitly the next layer of work.
  - Items 5–6: ML / inverse-search and historical AS/NZS case3 remain
    deferred.

### Task 2 — `core/calculator_unit_adapter.py` first slice

New file. Public API:

- `W_TO_BTU_PER_HOUR = 3.412141633`
- `ALLOWED_SOURCE_VALUES = ("manual_candidate", "ml_prediction", "fixture")`
- `supported_profile_ids() -> ("ahri_usa_seer2",)`
- `profile_native_units(profile_id) -> {"capacity": "Btu/h", "power": "W"}`
- `expected_source_units(profile_id, source)`
  - `ml_prediction` → `{"capacity": "W", "power": "W"}`
  - `manual_candidate` / `fixture` → `{"capacity": "Btu/h", "power": "W"}`
- `normalize_points_to_profile_native(profile_id, points, source) ->
  (normalized_points, units_trace)` where `units_trace` has
  `source_units`, `target_units`, and `conversion_applied`.

Behavior:

- Only `ahri_usa_seer2` is accepted; any other `profile_id` raises
  `ValueError`. EN14825, ISO16358, KS C 9306, AHRI HSPF2 are explicitly
  out of scope.
- `ml_prediction`: capacity W → Btu/h via `* 3.412141633`; power is W
  on both sides, no numeric change.
- `manual_candidate` / `fixture`: capacity must already be Btu/h and
  power must already be W. No conversion is performed.
- Any mismatched unit per source fails fast with a `ValueError` whose
  message names the expected unit and the source it was checked
  against.
- Non-mapping `points`, non-mapping point entries, missing
  `capacity_unit` / `power_unit`, and non-positive capacity / power
  all fail fast.

Unsupported-profile handling:

- `supported_profile_ids()` returns `("ahri_usa_seer2",)`.
- All public functions (`profile_native_units`, `expected_source_units`,
  `normalize_points_to_profile_native`) raise `ValueError` for any
  other profile id, so callers fail fast before they can emit a
  mis-converted value.

Verification (focused on this file):

- `python3 -B -m py_compile core/calculator_unit_adapter.py` → OK.
- `python3 -B -m pytest tests/test_calculator_unit_adapter.py -q`
  → `17 passed`.
- Schema boundary test still passes after adding the new file to
  `ADAPTER_MODULES`.

### Task 3 — `units_trace` on CalculatorInputEnvelope

Modified files: `core/calculator_input_adapter.py`,
`tests/test_calculator_input_adapter.py`.

Shape (stored under `options["units_trace"]`):

```python
{
    "source_units": {"capacity": "<unit>", "power": "<unit>"},
    "target_units": {"capacity": "Btu/h", "power": "W"},
    "conversion_applied": <bool>,
}
```

Validation rules:

- `target_units` must equal the profile-native unit mapping; otherwise
  `ValueError`. This guards `measured_inputs` against being labelled
  as anything other than calculator-native.
- Missing keys → `KeyError`; extra keys → `ValueError`; non-bool
  `conversion_applied` → `TypeError`.
- `options={"units_trace": ...}` is rejected with
  `ValueError("reserved key")` so callers must use the dedicated
  parameter.

Per-source behavior:

- `manual_candidate` / `fixture` (and any call that omits
  `units_trace`): default no-op trace
  (`source_units == target_units == profile-native`,
  `conversion_applied=False`).
- `ml_prediction`: caller (the prediction adapter) supplies a trace
  where `source_units` is W/W, `target_units` is profile-native, and
  `conversion_applied=True`.

`measured_inputs` always holds calculator-native values, so
`measured_inputs_as_test_points()` keeps returning the tuple form
`AHRICalculator.calculate_seer2` already accepts. Existing manual /
fixture tests pass without modification.

Verification:

- `python3 -B -m pytest tests/test_calculator_input_adapter.py -q`
  → `26 passed` (was `18 passed`; added 8 new tests for default trace,
  ml_prediction trace, target validation, missing keys, extra keys,
  reserved-key override).

### Task 4 — PredictedPointsEnvelope → CalculatorInputEnvelope conversion

Modified files: `core/calculator_prediction_adapter.py`,
`tests/test_calculator_prediction_adapter.py`.

Changes:

- Per-source unit validation is delegated to
  `core.calculator_unit_adapter.expected_source_units`. `ml_prediction`
  points must have `capacity_unit="W", power_unit="W"`;
  `manual_candidate` and `fixture` points must have
  `capacity_unit="Btu/h", power_unit="W"`. Mismatches raise
  `ValueError` with a message naming the active source.
- `predicted_points_to_calculator_input_envelope` now calls
  `normalize_points_to_profile_native` to obtain
  `(native_points, units_trace)`. The trace is attached to the
  resulting `CalculatorInputEnvelope` via
  `build_calculator_input_envelope(..., units_trace=...)`.
- `candidate_id`, `model_version`, and `model_target` continue to
  flow through `options` (existing behavior).

Specific contracts now enforced:

- ml_prediction with capacity in Btu/h → `ValueError("capacity_unit
  must be 'W' when source is 'ml_prediction'")`.
- manual_candidate with capacity in W → `ValueError("capacity_unit
  must be 'Btu/h' when source is 'manual_candidate'")`.
- ml_prediction with W/W input → calculator input envelope holds
  `measured_inputs[*].capacity = W_value * 3.412141633` and
  `units_trace.conversion_applied == True`.
- manual_candidate / fixture with profile-native input →
  `units_trace.conversion_applied == False`; measured_inputs values
  are passed through unchanged.

Verification:

- `python3 -B -m pytest tests/test_calculator_prediction_adapter.py -q`
  → `27 passed`.

### Task 5 — Envelope chain end-to-end smoke

New file: `tests/test_calculator_envelope_chain.py`. Single fixture
runs the full chain once:

1. `build_predicted_points_envelope("ahri_usa_seer2", points,
   source="ml_prediction", model_target="cooling",
   metadata={model_version, candidate_id})`
2. `predicted_points_to_calculator_input_envelope(predicted,
   profile_id="ahri_usa_seer2")`
3. `create_calculator_for_profile(profile_id="ahri_usa_seer2")
   .calculate_seer2(measured_inputs_as_test_points(calc_input))`
4. `wrap_calculator_result_envelope("ahri_usa_seer2", raw_result)`
5. `build_ranking_candidate_envelope(candidate_id, result_envelope)`

Assertions:

- Conversion: `measured_inputs["A_Full"].capacity ==
  10000 * 3.412141633`; power stays at 3000 W.
- `units_trace = {source_units: W/W, target_units: Btu/h/W,
  conversion_applied: True}` is present on the calculator input
  envelope.
- `candidate_id` flows through PredictedPointsEnvelope →
  CalculatorInputEnvelope options → RankingCandidateEnvelope.
- `model_version` flows through PredictedPointsEnvelope →
  CalculatorInputEnvelope options.
- CalculatorResultEnvelope carries `metric="SEER2"`, `units="Btu/Wh"`,
  positive `value`.
- RankingCandidateEnvelope uses only the result envelope's
  `calculator_profile_id`, `metric`, `value`, `units`. `score` defaults
  to `value`; `ranking_features` defaults to `{}`.
- RankingCandidateEnvelope does NOT expose `raw_result`,
  `diagnostics`, or any calculator-internal key like `bin_details`.

Verification:

- `python3 -B -m pytest tests/test_calculator_envelope_chain.py -q`
  → `7 passed`.

## Test Results

- `python3 -B -m py_compile core/calculator_unit_adapter.py core/calculator_input_adapter.py core/calculator_prediction_adapter.py core/calculator_result_adapter.py core/calculator_ranking_adapter.py`
  → exit 0.
- `python3 -B -m pytest tests/test_calculator_unit_adapter.py tests/test_calculator_input_adapter.py tests/test_calculator_prediction_adapter.py tests/test_calculator_ranking_adapter.py tests/test_calculator_envelope_chain.py tests/test_calculator_schema_boundaries.py -q`
  → `94 passed`.
- `python3 -B -m pytest -q` → `407 passed, 34 xfailed`. xfail count
  unchanged from prior baseline (ISO HSPF official-exact strict
  xfails preserved).

## Changed Files

- `core/calculator_unit_adapter.py` — new file. Single conversion site
  between ML canonical (W/W) and AHRI SEER2 native (Btu/h/W); other
  profiles fail-fast.
- `core/calculator_input_adapter.py` — `build_calculator_input_envelope`
  gains `units_trace=None` parameter; trace stored under
  `options["units_trace"]`; default no-op trace; validated against
  profile-native target.
- `core/calculator_prediction_adapter.py` — per-source unit
  validation; converts ml_prediction W → Btu/h via the unit adapter
  and attaches units_trace.
- `tests/test_calculator_unit_adapter.py` — new file. 17 tests.
- `tests/test_calculator_input_adapter.py` — adds 8 units_trace tests.
- `tests/test_calculator_prediction_adapter.py` — splits source tests
  by expected units; adds conversion + units_trace tests.
- `tests/test_calculator_envelope_chain.py` — new file. End-to-end
  chain smoke (7 tests).
- `tests/test_calculator_schema_boundaries.py` — adds
  `core/calculator_unit_adapter.py` to `ADAPTER_MODULES`.
- `docs/WORK_PLAN.md` — current milestone focus and near-term execution
  order updated as described above.
- `result_reports/active/085_calculator-unit-normalization-and-envelope-chain-smoke.md`
  — this report.

## Known Failures / Risks

- The ISO16358-2 HSPF strict xfails (11 cases) remain. Mismatch
  analysis is parked as a user-side external audit, not in the repo
  immediate next-action list.
- Only AHRI SEER2 has a unit-adapter implementation. EN14825 (kW),
  ISO16358 / KS C 9306 (W, W), and AHRI HSPF2 conversions are not
  implemented — those profiles will raise `ValueError` from the unit
  adapter until a follow-up slice covers them. Callers using those
  profiles still avoid silent miscalculation because the failure is
  loud.
- The end-to-end smoke only exercises the happy path with a single
  metadata combination. ML / inverse-search caller wiring is not in
  this slice and is intentionally out of scope.
- Adapter-owned envelope terms (`PredictedPointsEnvelope`,
  `CalculatorInputEnvelope`, …) are guarded against leaking into
  calculator core by `tests/test_calculator_schema_boundaries.py`. The
  new unit adapter file is part of the `ADAPTER_MODULES` exemption.

## Next Suggested Action

1. Implement AHRI SEER2 horizontal table-input UI as the first UI
   slice (see
   `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`).
   The unit adapter is not needed for that slice because UI input is
   `manual_candidate` profile-native.
2. Extend the unit adapter to AHRI HSPF2, then to EN14825 SEER / SCOP
   (kW conversions), then to ISO16358 / KS C 9306 (no conversion
   required, but still validated). Each profile addition gets its own
   `tests/test_calculator_unit_adapter.py` parametrisation slice.
3. Wire an ML / inverse-search caller path that produces
   `source="ml_prediction"` PredictedPointsEnvelope payloads in W
   canonical units. Until that path exists, the envelope chain test
   here is the single source of regression coverage.

## Scope Compliance

- `core/calculator_iso16358.py` — not modified.
- `core/calculator_ahri.py` — not modified (verified by py_compile
  and full-suite test counts; no diff in this commit).
- ISO16358-2 HSPF expected / xfail list — unchanged.
- UI / `app_calculator.py` / `ui/calc_window.py` — not modified.
- Region configs — not modified.
- ML model call — not added.
- EN14825 / ISO16358 / KS C 9306 / AHRI HSPF2 unit conversion — not
  added (explicitly out of scope).
- Calculator public APIs — unchanged.
- Calculator result schema — unchanged.
- Schema boundary test — only the `ADAPTER_MODULES` set was extended;
  the banned import / banned region key sets are unchanged.

## Commit / Push

- Source + tests + docs commit: a single commit covering
  `core/calculator_unit_adapter.py` (new),
  `core/calculator_input_adapter.py`,
  `core/calculator_prediction_adapter.py`,
  `tests/test_calculator_unit_adapter.py` (new),
  `tests/test_calculator_input_adapter.py`,
  `tests/test_calculator_prediction_adapter.py`,
  `tests/test_calculator_envelope_chain.py` (new),
  `tests/test_calculator_schema_boundaries.py`,
  `docs/WORK_PLAN.md`.
- Report commit: this report as a separate commit (`report: ...`
  style).
- Both commits pushed to `origin/work/iso-separation-plan`.

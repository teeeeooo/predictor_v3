# 082 Summary: Envelope Adapter Four-Stage Chain (Audit 4/5)

## Covered Reports

- `069_hspf2-ui-duplicate-row-guard.md`
- `070_wire-en14825-ui-to-scop.md`
- `071_calculator-input-envelope-adapter-slice.md`
- `072_strengthen-calculator-schema-boundary-guards.md`
- `073_audit-4-next-actions-completion.md`
- `074_sync-active-docs-after-audit4.md`
- `075_align-calculator-input-envelope-with-design.md`
- `076_en14825-seer-profile-ui-wiring.md`
- `077_ahri-hp-hspf2-ui-happy-path-smoke.md`
- `078_predicted-points-envelope-adapter-slice.md`
- `079_ranking-candidate-envelope-min-smoke.md`
- `080_audit-5-next-actions-completion.md`

## Workstream Summary

### HSPF2 UI guard + EN14825 SCOP wiring (069, 070, 077)

- Added regression smoke around the HSPF2 input form (`069`) and a
  happy-path smoke that confirms AHRI HP mode emits both SEER2 and
  HSPF2 v3 strings in the shared result label (`077`).
- Replaced the EN14825 tab placeholder `calculate_en()` with a real
  `calculate_scop()` call path (`070`). UI takes A/B/C/D/TOL/Tbiv +
  p_design_h + climate + standby (W) inputs and W→kW conversion lives in
  the UI adapter, not in the calculator.

### CalculatorInputEnvelope first slice + design alignment (071, 075)

- Landed the first `CalculatorInputEnvelope` slice for `ahri_usa_seer2`
  in `core/calculator_input_adapter.py` (`071`).
- Re-shaped the slice to match
  `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`:
  top-level `{calculator_profile_id, standard, region, mode, metric,
  measured_inputs, options}` with profile-derived identity fields,
  dict-shaped `measured_inputs`, options-bag for units / source, locked
  source vocabulary `manual_candidate / ml_prediction / fixture`,
  fail-fast on extra keys, and a `measured_inputs_as_test_points` helper
  that keeps calculator public APIs unchanged (`075`).

### Schema boundary guard expansion (072)

- Added `candidate_id, predicted_points, calculator_input,
  calculator_result, ranking, ranking_features` to the banned region
  config keys and adapter-owned terms in
  `tests/test_calculator_schema_boundaries.py`.

### EN14825 SEER profile + UI metric-aware branch (076)

- New `en14825_seer` calculator profile reusing the EN14825 SCOP config
  path (SEER does not consume SCOP-specific JSON keys).
- EN tab now exposes both SCOP and SEER profile selections; UI tracks
  `self.en_profile` and `calculate_en()` branches into `calculate_seer`
  or `calculate_scop` based on profile metric. SCOP path behavior is
  preserved.

### PredictedPointsEnvelope first slice (078)

- New `core/calculator_prediction_adapter.py` validates predicted points
  per design doc shape (per-point capacity_unit / power_unit, locked
  source / model_target vocabulary, metadata key whitelist) for
  `ahri_usa_seer2` and converts into a CalculatorInputEnvelope through
  the existing input adapter without unit conversion.

### RankingCandidateEnvelope minimum smoke (079)

- New `core/calculator_ranking_adapter.py` consumes
  `CalculatorResultEnvelope` and produces a minimal
  `{candidate_id, calculator_profile_id, metric, value, units, score,
  ranking_features}` envelope. `score` defaults to the metric value;
  `raw_result` and `diagnostics` are intentionally not exposed. Ranking
  layer must consume envelope fields, not raw calculator dicts.

### Doc sync + audit closures (073, 074, 080)

- Synced `project_log.md`, `docs/WORK_PLAN.md`, and `project_brief.md`
  to the audit_4 completion state so future agents see the realized
  envelope adapter state and queued next steps.
- Closed audit 4 (`073`) and audit 5 (`080`) next-action cycles with
  per-cycle completion reports force-added under `reference_files/`.

## Decisions Preserved

- `CalculatorInputEnvelope` is locked to the design doc shape:
  `{calculator_profile_id, standard, region, mode, metric,
  measured_inputs, options}`; `source` lives in `options["source"]`.
- `source` vocabulary is `manual_candidate / ml_prediction / fixture`
  across input and predicted-points adapters; legacy `manual / predicted`
  are rejected.
- Envelope adapters do not perform unit conversion. AHRI SEER2 capacity
  must be `Btu/h` and power must be `W`; mismatches fail fast.
- AHRI SEER2 is the single supported profile across input / predicted /
  ranking adapter slices. EN / KS / ISO profile coverage is deferred to
  follow-up slices.
- RankingCandidateEnvelope is the only path ranking layers consume;
  raw calculator output is not re-exposed downstream.
- EN14825 SEER reuses the SCOP region config JSON because the SEER
  path does not consume SCOP-specific static keys.
- Region configs are statically guarded against runtime / ML / ranking
  vocabulary by the boundary tests; `ADAPTER_MODULES` is the only
  exemption set.

## Verification Snapshot

- Latest full suite recorded in covered report `080` (audit 5
  completion): `364 passed, 23 xfailed`.
- Adapter focused subset (input / result / predicted / ranking /
  boundary / profiles / dispatcher / EN golden / AHRI SEER2 smoke / UI
  smoke) recorded in `080`: `112 passed`.

## Archive Candidates

Move covered active reports `069` through `080` to
`result_reports/archive/` without renaming.

## Project Log Sync Judgment

`project_log.md` update is recommended (and performed in the same
lifecycle maintenance commit) to record the audit_5 completion entry.
Audit 4 already has a completion block; audit 5 introduced (a) the
locked envelope shape and source vocabulary, (b) the new
PredictedPointsEnvelope / RankingCandidateEnvelope adapter slices, and
(c) the EN14825 SEER profile metric-aware UI branch — these are
adapter-layer architecture / contract decisions that future agents
should be able to recover from `project_log.md` alone.

# 624 Arc 13 ML Feature Manifest Design Gate

## Goal

Create the Arc 13 Slice 0 design/audit record for a minimal ML feature manifest
foundation without changing production runtime behavior.

## Scope

- Audited current ML feature owners and prediction adapter touchpoints.
- Defined the user-managed CSV boundary and code-derived/developer-managed
  boundary.
- Proposed minimal schema, projection strategy, validator requirements, and
  staged migration plan.
- Updated near-term Arc 13 planning docs and design index.

## Changed Files

- `docs/designs/2026-06-30-arc13-ml-feature-manifest-design-gate.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/624_arc13-ml-feature-manifest-design-gate.md`

## Verification

- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict`:
  OK.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 129 passed and 1286 deselected.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK,
  reference map fresh; commit hash and dirty-worktree notes were informational.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing soft
  warnings outside this docs-only slice.
- `git diff --check`: OK.

## Known Risks

- Runtime zero-fill behavior remains broader than the target
  `zero_fill_policy`; this is documented but intentionally unchanged.
- Manifest projection parity is not implemented in Slice 0.
- Real model prediction quality is not validated by this docs/audit slice.

## Commit / Push

- Commit and push are performed after report finalization. Final publication
  verification is reported in terminal output.

## Project Memory Delta

- type: decision
  topic: Arc 13 ML feature manifest foundation
  content: Arc 13 begins with a design/audit slice for a single-file ML feature
    manifest boundary; runtime constants, registry behavior, predictor schema,
    and inference zero-fill behavior remain unchanged until implementation
    slices add validator and parity tests.
  keywords: arc13, ml-feature-manifest, feature-catalog, zero-fill-policy,
    predictor-schema, model-registry

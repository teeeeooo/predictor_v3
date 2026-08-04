record:
  date: 2026-08-05
  topic: active-documentation-target-policy-owner-correction
  tags: documentation, architecture, target-policy, leakage, registry, correction
  memory_review: no-change
  memory_reason: Existing Phase 4G memory already records Target as the writable input-policy owner and MODEL_REGISTRY as a generated compatibility facade.

# Active Documentation Target Policy Owner Correction

## Change Reason

Fresh PR #52 audit found one active architecture contradiction: the Data Leakage
section routed target-specific leakage policy to `core/ml/registry.py` even though
the same architecture owner and current source place that policy in canonical
Data Definition Target ownership.

## Contract / Behavior Changed

- Route target-specific allowed/exclude input policy to canonical
  `TargetDefinition.policy_mode` / `policy_owner_identities`.
- Describe generation-bound `RuntimeTarget` / `ModelRegistrySnapshot` as the
  runtime projection consumed through `core/data_definition/target_registry`.
- State explicitly that `core/ml/registry.py::MODEL_REGISTRY` is a generated
  compatibility facade, not the production Target/leakage policy owner.

## Evidence And Verification

- Same-document owner comparison: `project_architecture.md` now agrees between
  Data Leakage guidance and the Canonical Target registry section.
- Current source comparison: `TargetDefinition` owns `policy_mode` and
  `policy_owner_identities`; `RuntimeTarget` projects owner identities to
  `policy_ml_names`; `apply_target_policy()` applies that runtime projection.
- `core/ml/registry.py::MODEL_REGISTRY` remains generated from
  `model_registry_snapshot(bootstrap_manifest())` and is compatibility-only.
- Existing Phase 4G memory already records Target as the writable identity-policy
  owner and `MODEL_REGISTRY` as a generated compatibility facade, so no memory
  update is required.
- `git diff --check` — PASS for this bounded correction.
- `python3 -B -m tools.check_agent_change_gate --cached` — PASS
  (`agent change gate: OK`) with the correction record and discovery index staged.

## Changed Files

- `docs/architecture/project_architecture.md`
- `result_reports/REPORT_INDEX.md`
- this correction record

The original Active Documentation Contract Restoration records remain unchanged;
this correction narrows only their current-owner restoration evidence for Target
input/leakage policy.

## Known Risks

No Target policy behavior, source, tests, runtime, config, or broader PR #52
restoration owner was changed. Fresh independent Lane C exact-head re-audit of
PR #52 remains required.

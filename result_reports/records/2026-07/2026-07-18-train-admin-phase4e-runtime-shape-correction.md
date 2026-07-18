# Train/Admin Phase 4E Runtime Operand Shape Correction

```yaml
record:
  date: 2026-07-18
  topic: train-admin-phase4e-runtime-shape-correction
  tags: train-admin, phase-4e, derived-feature, final-audit, runtime-shape, validation, publication
  memory_review: updated
  memory_reason: Exact pre-evaluator role/source shapes are a durable eligibility invariant for authoring, publication, and runtime snapshots.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The core eligibility owner checked a supported role and model-input flag but did
not bind that role to its runtime value source. A raw or historical manifest could
therefore disguise a post-evaluator formula/result/status value as an input-like
Feature and pass Derived validation.

## Contract / Behavior Changed

- The existing pure core policy now permits Feature operands only for exact
  `input/manual`, `auto/mapping_lookup`, and `one_hot_feature/one_hot` shapes,
  together with the existing active, numeric, ML-name, model-input, and non-Target
  requirements.
- Role/source mismatches return `derived_operand_runtime_unavailable` with stable
  identity, ML name, and an actionable reason containing both fields. Existing
  Target/result, inactive, and type/name classifications retain priority.
- Commands, whole-contract validation, legacy normalization validation,
  application options, and evaluator snapshot creation continue to consume the
  same policy. No secondary shape table or runtime provider was added.
- Immutable publication rejects the invalid candidate before staging or pointer
  mutation; valid v1 read/rollback compatibility remains unchanged.

## Evidence And Verification

- Policy tests cover all three allowed shapes and thirteen rejected role/source
  combinations with identity, ML-name, code, and reason evidence.
- Add and Edit reject every invalid shape in numerator and denominator positions,
  retain the original draft, and default-inactive Add remains blocked. Enable also
  rejects a fabricated invalid inactive relation.
- Raw v2 and normalized v1 manifests fail whole-contract validation and snapshot
  creation. Repository publication preserves the active generation, creates no
  candidate generation, and leaves no staging or pointer temporary residue.
- Controller/UI tests project the disguised Feature as disabled and expose the
  policy code/reason without adding View-side role/source logic.
- Focused Phase 4E/publication/UI tests pass with `142 passed`; broader Data
  Definition regression passes with `215 passed`; the full repository suite
  passes with `2352 passed, 2 xfailed`.

## Changed Files

- core Derived operand eligibility policy
- focused core command/contract/migration, repository publication, and UI tests
- active architecture, work-plan, project-log, memory, and result-record owners

## Known Risks

- Phase 4H remains the runtime generation cutover owner and is not implemented
  here.
- Windows native UI smoke was not run and remains a pre-release verification item.

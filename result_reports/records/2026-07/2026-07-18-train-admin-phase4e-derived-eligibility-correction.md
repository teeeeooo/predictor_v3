# Train/Admin Phase 4E Derived Eligibility Correction

```yaml
record:
  date: 2026-07-18
  topic: train-admin-phase4e-derived-eligibility-correction
  tags: train-admin, phase-4e, derived-feature, audit-correction, eligibility, leakage, dependency-projection, predict
  memory_review: updated
  memory_reason: The single eligibility and runtime dependency owner is a durable Phase 4E boundary needed by authoring, Train, and Predict.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Phase 4E validated numeric identity operands but did not distinguish values
available before Derived evaluation from Target/result outputs. Predict separately
expanded any Derived requirement with a fixed six-name set. The split allowed
leakage definitions and prevented new valid numeric operands or Derived chains
from projecting their real runtime inputs.

## Contract / Behavior Changed

- One pure core policy returns eligibility, stable identity, ML name, owner/source,
  blocked code, and user-facing reason. Active numeric manual, mapping-backed, and
  pre-evaluator one-hot Features are eligible; Result/Target, formula/result/status,
  inactive, nonnumeric, nameless, and unavailable owners are blocked.
- Derived commands and whole-contract validation use that policy. Invalid operands
  are rejected even when the authored definition is inactive, while identity DAG,
  active Derived dependency, cycle, missing identity, and existing eight-definition
  behavior remain intact.
- The application/controller projects selectable and blocked operand options. The
  View displays the projection, disables blocked options with reasons, and submits
  only identities; it no longer checks source kind, type, or ML-name eligibility.
- The immutable evaluator snapshot projects requested output identities or names
  through the active Derived closure to deterministic, deduplicated base Feature
  inputs. Predict consumes that projection instead of a fixed dependency constant,
  and evaluates only the required Derived closure.
- Train and Predict classify missing evaluator inputs through the same projection.
  Predict retains catalog-approved zero fill before the shared missing check; all
  other missing inputs fail actionably before evaluator lookup.

## Evidence And Verification

- Command and raw-manifest tests block Heating Power, Cooling Power, Ref Qty, and
  Cooling Hz leakage operands with the Result/Target code. Eligibility tests cover
  manual, mapping-backed, one-hot, inactive, nonnumeric, nameless, and unavailable
  Feature owners; the existing eight definitions remain valid.
- Dependency tests cover direct Feature inputs, a new numeric Feature, a two-level
  Derived chain, shared-base deduplication, deterministic ordering, identity/name
  requests, inactive exclusion, and non-Derived requests.
- Predict calculates the custom chain from its transitive base inputs and reports a
  missing new source before evaluator execution. Existing zero-fill behavior and
  all eight Train/Predict output values remain covered.
- Focused Phase 4E/ML/UI tests pass with `85 passed`; Phase 4B–4D Data Definition
  regression passes with `171 passed`; the full repository suite passes with
  `2308 passed, 2 xfailed`. Structure validation has no hard failure and reports
  only warning-level existing hotspots.

## Changed Files

- core Derived eligibility, contract validation, evaluator snapshot/dependency
  projection, and Train/Predict preprocessing adapters
- Data Definition controller operand presentation and restricted Derived dialogs
- focused core/application/UI/runtime regressions and active owner documentation

## Known Risks

- Phase 4H still owns runtime generation cutover. This correction uses the current
  immutable snapshot adapter and does not introduce a process-wide provider.
- Windows native UI smoke was not run and remains a pre-release verification item;
  offscreen automation does not replace that evidence.

```yaml
record:
  date: 2026-07-12
  topic: ahri-core-refactor-contract-lock
  tags: ahri210240, seer2, hspf2, architecture, golden, refactor
  memory_review: no-change
  memory_reason: The active design and AHRI owner documents are direct discovery sources; existing memory already preserves separate AHRI ownership and stable contracts.
```

# Change Reason

AHRI variable-capacity SEER2/HSPF2 must be decomposed before multi-capacity work without changing the canonical calculator behavior shared by Calculator and ML paths.

# Contract / Behavior Changed

The approved internal boundary is stable public facades over private context, point, variable-capacity, and legacy owners. Existing public imports, methods, constructor-visible attributes, result/diagnostics mappings, exceptions, formula behavior, and user-confirmed official-calculator golden expected values remain unchanged.

# Evidence And Verification

R0 adds facade signature/attribute guards and canonical deep-result fingerprints for representative HSPF2 v3, HSPF2 v2, and SEER2 results. The fingerprints are structural characterization evidence, not new official golden data.

# Changed Files

The design record, AHRI owner notes, compact contract tests, this record, and the result index establish the refactor baseline. Subsequent slices implement the approved private owners behind the locked facade.

# Known Risks

Full-result fingerprints are intentionally strict and may require focused diagnosis if Python serialization behavior changes. They must not be updated merely to accommodate refactor drift.

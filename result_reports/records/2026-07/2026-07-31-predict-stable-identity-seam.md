record:
  date: 2026-07-31
  topic: predict-stable-identity-seam
  tags: predict, data-definition, stable-identity, runtime-descriptor, generation-migration
  memory_review: no-change
  memory_reason: Existing memory already records Data Definition identity ownership and identity-based Predict generation migration; the active architecture owner now records the application seam.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The canonical `FeatureDefinition.identity` reached Predict generation migration
but was discarded by the identity-free generated schema row before the final
application and presentation descriptors. Downstream Input and Result surfaces
therefore could not retain one canonical Feature association across generation
rename, ordering, visibility, or membership changes.

# Contract / Behavior Changed

Predict application now owns one frozen generation-bound column descriptor. It
derives identity only from the canonical manifest and Predict identity ordering,
keeps current key/label and presentation metadata separate, and fail-fast checks
that the existing generated projection is complete and semantically equal.
Qt-free schema adapters carry the descriptor into the unified case-table
contract. Status and message remain app-virtual columns without Feature identity.
Both standalone and Train-embedded composition use the same runtime snapshot and
adapter path.

# Evidence And Verification

- Narrow descriptor and generation-migration suite: 12 passed.
- Generation projection, Predict/Train participant migration, schema/application,
  and standalone/embedded presentation suite: 58 passed.
- Changed-source compilation, Qt-free descriptor/schema import, and
  `git diff --check`: passed.
- Cached staged-change gate: passed.
- Repository structure check passed with 33 warnings on unchanged existing
  hotspots; no changed file produced a structure warning.

# Changed Files

- Predict runtime column contract, snapshot composition, and schema adapters.
- Focused identity, generation mutation, migration, schema, and composition tests.
- Train/Predict architecture owner and current work plan.
- This compact record and its discovery index row.

# Known Risks

- The public/generated Predict schema and persisted Feature Definition shape
  intentionally remain identity-free/unchanged; application identity is available
  only through a complete generation-bound runtime snapshot.
- Typed result context, stale-result provenance, Result Review, `사양 요약`,
  EER/COP, Layout B, bulk paste, and Calculator integration remain later slices.
- No production generation, model, mapping, user data, or lifecycle artifact was
  mutated.

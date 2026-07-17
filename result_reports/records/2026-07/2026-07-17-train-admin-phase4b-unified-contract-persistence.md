# Train/Admin Phase 4B Unified Contract Persistence

```yaml
record:
  date: 2026-07-17
  topic: train-admin-phase4b-unified-contract-persistence
  tags: train-admin, phase-4b, canonical-manifest, generation-bundle, atomic-pointer, fingerprints, data-definition
  memory_review: updated
  memory_reason: The durable Phase 4 state now includes the implemented canonical manifest, generation publication, rollback, and protected-consumer Save boundary.
```

## Change Reason

The distributed Predict schema, ML catalog, Derived policy, One-hot policy,
Target registry, and Mapping requirements had no single persistence owner, so an
ML-projection-changing Definition Save could not be published safely.

## Contract / Behavior Changed

- `config/data_definition/manifest.json` is the deterministic repository
  bootstrap for `unified_feature_contract.v1`; compatibility names remain
  projections while managed objects receive stable opaque identities.
- One manifest generates Predict schema, ordered ML catalog, Derived runtime,
  One-hot runtime, Target/registry, and Mapping-requirement projections and all
  projections carry or prove one generation identity.
- Scoped fingerprints distinguish combined, Predict, ordered ML, Derived,
  One-hot, Target/registry, Mapping-requirement, and preprocessing compatibility.
- The Train filesystem adapter stages and validates a complete generation,
  publishes its immutable directory, then atomically replaces the active pointer.
  Prior generations remain readable and rollback-capable.
- The Data Definition application service can publish a complete canonical
  generation. It replaces the legacy full-parity blocker only for validated
  model-compatible projection changes; protected ML/fixed-string blockers remain.
- Concrete `mapping.json`, model artifacts, promotion, training execution, and
  runtime cutover are excluded from the transaction.

## Evidence And Verification

Automated tests cover deterministic bootstrap and JSON round-trip, current
Predict/ML/Derived/One-hot/Target/Mapping parity, whole-contract rejection,
order-sensitive and presentation-only fingerprints, immutable publication,
staging and pointer failure injection, active-generation preservation, complete
bundle reads, rollback, guarded Save integration, and existing Data Definition
compatibility behavior. POSIX same-filesystem `os.replace` plus file/directory
`fsync` is the selected atomic primitive for the supported macOS environment.

## Changed Files

- canonical manifest and bootstrap CLI
- `core/data_definition/contract/` domain contract package
- Train generation repository adapter and persistence application service
- Data Definition service compatibility integration
- focused acceptance tests and active owner/status documents

## Known Risks

- Import-time Train/Predict/ML consumers are not cut over in Phase 4B; protected
  ML-name/order/One-hot/Derived/Target changes remain blocked.
- Atomic publication assumes staging and final generation directories share one
  filesystem. Cross-filesystem stores are not supported by this adapter.
- Phase 4H still owns process-wide runtime cutover and standalone Predict reload.

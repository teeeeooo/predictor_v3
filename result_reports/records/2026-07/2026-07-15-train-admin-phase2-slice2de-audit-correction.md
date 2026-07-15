```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase2-slice2de-audit-correction
  tags: train-admin, mapping, phase-2, slice-2d, slice-2e, validation, semantic-noop, rollback
  memory_review: updated
  memory_reason: Preserve the canonical import validation, row-order no-op, affected-count, and partial-publish rollback contracts for re-audit.
```

# Change Reason

Draft PR #15 audit found that structurally valid exchange candidates could
bypass canonical Data Mapping validation, preview counts did not reflect real
changes, CSV row order could create dirty/undo state, and publish rollback was
not exercised after a partial target replacement.

# Contract / Behavior Changed

- Candidate parsing reuses canonical editor validation before preview; the
  service adds its Data Definition requirement/group projection and repeats the
  complete validation at Apply.
- Existing validation issues remain the blocker metadata and invalid or stale
  previews cannot mutate draft, baseline, history, or runtime files.
- Affected groups count only added, removed, or changed rows.
- Matching identities retain current order while new identities use sorted
  canonical identity order, making row-order-only bundles semantic no-ops.
- Export implementation remains unchanged; regression now proves best-effort
  rollback after three successful publishes for existing and mixed packages.

# Evidence And Verification

- Focused exchange import/export and preview UI: 46 passed.
- Impacted mapping and Train regression: 143 passed.
- Full repository suite: 2064 passed, 2 expected failures.
- Native macOS interaction was not retried because the desktop remains locked;
  no PNG or physical-interaction acceptance is claimed.

# Changed Files

- Exchange candidate/import owners and Data Mapping service/preview DTO.
- Focused import/export regression tests.
- Work plan, native manifest automated result, memory, and record index.

# Known Risks

- Rollback is still best-effort when the operating system also prevents backup
  restoration; no stronger atomicity claim is made.
- Native Slice 2B+2C physical interaction and Slice 2D+2E visual evidence remain
  deferred under the existing locked-desktop blocker.

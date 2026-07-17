# Train/Admin Phase 4B Final Audit Correction

```yaml
record:
  date: 2026-07-17
  topic: train-admin-phase4b-final-audit-correction
  tags: train-admin, phase-4b, windows, cross-process-lock, explicit-persistence, predict-order, runtime-state
  memory_review: updated
  memory_reason: Windows process locking, explicit persistence selection, and runtime-state ownership are durable production invariants.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
```

## Change Reason

The corrected Phase 4B adapter imported POSIX-only `fcntl`, constructor defaults
could silently recreate the legacy writer, and duplicate Predict
`display_order` values could pass canonical validation. Runtime generation state
also needed a clear boundary from tracked source config for the Windows-primary
deployment.

## Contract / Behavior Changed

- The filesystem adapter lazily selects native `flock` on POSIX or
  `msvcrt.locking` on Windows and holds one process lock from parent comparison
  through immutable publication and active-pointer replacement. The persistent
  coordination file avoids unlink/inode races; staging and pointer temporary
  files are removed on failure.
- `DataDefinitionService` accepts exactly one explicit persistence owner:
  canonical generation repository or legacy `schema_path`. Controller, panel,
  and Train shell construction no longer invent an implicit legacy owner.
- Production `create_shell()` retains canonical bootstrap/publication wiring.
  Runtime generation history and the active pointer default to per-user state:
  `%LOCALAPPDATA%\\predictor_v3\\data_definition` on Windows and the XDG state
  root (or `~/.local/state`) on POSIX. The tracked manifest remains the canonical
  bootstrap seed, and the former source-config runtime directory is ignored.
- Predict `display_order` must be unique and within 1..2147483647 across all
  Features, including inactive Features because canonical Predict ordering also
  includes them. Storage order, canonical ordering, display sorting, projection,
  and consumer-loader order must agree.

## Evidence And Verification

The impacted Phase 3/4B suite passes 276 tests. It covers production composition,
bootstrap, publication, stale rejection, rollback, lock/publication failure
preservation, explicit compatibility construction, duplicate/range ordering,
projection/consumer parity, protected Save guards, and Phase 3 UI regressions.
The complete repository suite passes 2247 tests with 2 existing expected
failures.
On the POSIX development host, a spawn-based two-process contention test proves
that exactly one candidate publishes. A subprocess also proves Train app and
adapter import when `fcntl` import is forbidden. The Windows code path is covered
with a simulated `msvcrt` lock backend through bootstrap, publication, stale
rejection, and rollback; this is not a native Windows execution claim.

## Known Risks

- Native Windows Train import/bootstrap/Save and real two-process contention
  still require a Windows CI runner or packaging smoke before release. No
  installer or migration workflow is introduced by this correction.
- Runtime cutover, standalone Predict reload, authoring UI, model promotion, and
  Data Mapping dirty-draft reconciliation remain later slices.
- Phase 4C may start after this corrected PR is merged and must preserve the
  existing protected-consumer guards until explicit dependency migration exists.

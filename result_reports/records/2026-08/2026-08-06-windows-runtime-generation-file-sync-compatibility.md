record:
  date: 2026-08-06
  topic: windows-runtime-generation-file-sync-compatibility
  tags: runtime-generation, windows, fsync, durability, atomic-publication, bootstrap
  memory_review: updated
  memory_reason: The Phase 4B Windows simulation did not model the writable-descriptor requirement of Windows file fsync.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Clean Windows first-run generation bootstrap failed before publication because
the shared runtime-generation repository called `os.fsync()` on files opened
read-only. Existing Windows simulation selected the `msvcrt` lock backend and
skipped directory fsync, but host POSIX file-sync behavior hid this restriction.

# Contract / Behavior Changed

- Runtime-generation file durability opens staging-bundle and active-pointer
  temporary files read/write on Windows before `fsync`.
- POSIX retains its existing read-only file-sync descriptors and directory
  durability calls.
- Immutable bundles, hash verification, the single-writer lock, stale-parent
  rejection, rollback, same-filesystem rename, and atomic active-pointer
  replacement are unchanged.
- Train and Predict first-run composition and execution-triggered headless
  Experiment initialization share the repaired repository. Calculator remains
  independent of runtime-generation bootstrap.

# Evidence And Verification

The repository regression models a Windows-like `Bad file descriptor` failure
for every read-only descriptor passed to `fsync`. It exercises initial and
subsequent bundle staging, active-pointer publication, stale rejection,
Windows lock/unlock balancing, and rollback, and proves that both staging and
pointer files reach the compatible sync path. Existing POSIX publication and
cross-process tests retain their original semantics. Native Windows execution
evidence remains unavailable and must not be inferred from simulation.

# Changed Files

The change is limited to the shared runtime-generation filesystem adapter, its
direct repository regression, this record/index, and the matching Phase 4B
memory correction.

# Known Risks

Separate model-lifecycle candidate/export persistence owners also contain
read-only file-sync patterns and broader directory-descriptor assumptions.
They are not part of runtime-generation publication and require a separately
scoped Windows portability lane before claiming those operations are native
Windows compatible.

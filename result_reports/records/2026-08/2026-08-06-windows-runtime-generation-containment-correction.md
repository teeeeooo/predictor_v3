record:
  date: 2026-08-06
  topic: windows-runtime-generation-containment-correction
  tags: runtime-generation, windows, bootstrap-recovery, containment, substitution, generation-id, correction
  memory_review: updated
  memory_reason: Runtime-generation bootstrap recovery now has an explicit external-no-mutation substitution boundary and complete Windows filename portability rules.
change_gate:
  new_source: justified
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: local-with-reason

# Change Reason

Fresh audit of PR #56 showed that bundle-marker-free recovery validated nested
entries but still wrote through the generation pathname itself. A generation
root symlink therefore redirected bootstrap reconstruction into an external
directory. The same audit also found that Generation ID validation did not reject
Windows device/reserved aliases, trailing dot/space, stream/colon, and other
reserved filename forms.

# Contract / Behavior Changed

- Incomplete-bootstrap recovery no longer trusts a validated pathname for later
  mutation. POSIX recovery mutates through an opened, identity-checked generation
  directory descriptor and exclusive relative file creation.
- Windows recovery rejects reparse/junction directories and pins the repository
  root, generations directory, generation directory, and projection directory
  with no-delete-sharing native handles across validation and mutation.
- Recovery validates residue again inside that boundary, creates only missing
  expected files exclusively, and publishes `bundle.json` last without clobbering
  a conflicting marker. Validation-to-mutation substitution cannot redirect
  writes into an external tree.
- Windows Generation IDs now reject the reserved filename semantics used by
  device names and aliases, including case/extension forms, superscript COM/LPT
  aliases, trailing dot/space, stream/colon, wildcard/separator/forbidden
  characters, and ASCII controls. Existing semantic/hash IDs remain valid.
- Canonical `/` bundle identity, separator-only legacy metadata compatibility,
  exact hash/fingerprint/projection validation, stale-parent rejection, rollback,
  single-writer locking, PR #53 writable-file sync, and ordinary POSIX behavior
  remain unchanged.

# Evidence And Verification

Direct regressions reproduce the audited symlink escape and model Windows
reparse attributes. Deterministic failure-hook attacks substitute either the
final generation directory or its generations parent after residue validation
but immediately before mutation; external trees remain byte-for-byte unchanged.
The Windows simulation proves the no-delete-sharing guard blocks the same attack,
and its native-call contract opens directory handles with `OPEN_REPARSE_POINT`
and without delete sharing. Reserved-name cases and normal generated IDs are
covered alongside matching/conflicting/corrupt recovery states.

Native Windows repaired-head execution is not available to this Worker and is
not promoted from macOS-hosted simulation.

# Changed Files

The correction adds one Runtime Generation owner-local recovery-containment
helper, adjusts the existing repository and direct regressions, reconciles the
canonical architecture owner and Phase 4B memory, and records this append-only
correction. Model Lifecycle and Deployment Export helpers are neither imported
nor modified.

# Known Risks

This correction is intentionally limited to the in-place incomplete-bootstrap
reconstruction boundary identified by audit. It does not redesign ordinary
Runtime Generation directory publication, active-pointer replacement, or writer
locking without direct evidence. Train Confirmation snapshot path serialization,
packaging/PyInstaller, and other persisted owners remain separately scoped.

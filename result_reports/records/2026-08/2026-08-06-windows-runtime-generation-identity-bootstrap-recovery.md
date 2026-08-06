record:
  date: 2026-08-06
  topic: windows-runtime-generation-identity-bootstrap-recovery
  tags: runtime-generation, windows, bundle-identity, bootstrap-recovery, containment, immutability
  memory_review: updated
  memory_reason: Runtime-generation persistence now has portable bundle/generation identity and bounded bootstrap-residue recovery semantics.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: local-with-reason

# Change Reason

Native Windows Train startup exposed two defects in the shared Data Definition
runtime-generation owner. Bundle metadata serialized host-native relative paths,
so Windows-created bundles failed their own canonical file-set check. An active
pointer to a missing or incomplete bootstrap generation then entered the
self-generation reuse path, which attempted to read the incomplete bundle and
surfaced the raw filesystem failure instead of reconstructing safe first-run
state.

# Contract / Behavior Changed

- New bundle metadata persists fixed `/`-separated relative file identities on
  every host. Reader compatibility normalizes only separator-only legacy Windows
  metadata in memory before the same exact file-set/hash/semantic validation;
  immutable legacy metadata is not rewritten.
- Generation IDs used by publish, direct reads, and the active pointer must be a
  single portable path component under both POSIX and Windows syntax. Rooted,
  drive-qualified, nested, traversal, or alternate-separator forms fail closed.
- If a parentless bootstrap candidate matches the active pointer, a valid
  complete immutable generation is reused. A missing generation or a directory
  without `bundle.json` is recoverable only when every extant owned file is
  byte-identical to the same bootstrap candidate and there are no unknown or
  link-like entries. Missing files are reconstructed and `bundle.json` is
  published last.
- A bundle marker plus hash/fingerprint/semantic corruption, or conflicting
  incomplete residue, is never silently overwritten or accepted.
- Existing stale-parent rejection, process writer locking, atomic pointer
  replacement, rollback, POSIX durability, and PR #53 Windows writable-file
  sync behavior remain the publication contract.

# Evidence And Verification

macOS-hosted tests explicitly model Windows path syntax and the existing Windows
`msvcrt`/writable-fsync branch. They cover canonical new metadata, immediate
self-read, legacy separator compatibility without hash relaxation, portable
Generation ID rejection, clean bootstrap, valid reuse, missing/incomplete
bootstrap recovery, unknown/conflicting residue, complete corruption, stale
writers, rollback, and Train/Predict startup composition. Native Windows is the
failure provenance only; it is not repair PASS evidence for this Worker.

# Changed Files

The bounded change touches the shared runtime-generation repository, its direct
and startup-composition regressions, the canonical architecture owner, this
record/index, and the existing Phase 4B memory entry. No Model Lifecycle,
Deployment Export, calculator, packaging, or ML algorithm owner changes.

# Known Risks

The same-owner inspection did not adopt Model Lifecycle or Deployment Export
native Windows root-handle pinning/write-through rename helpers. Those helpers
belong to separate persisted owners, and no native Runtime Generation failure or
owner-local substitution evidence in this slice justifies coupling or duplicating
their threat-hardening architecture. The directly evidenced containment gap was
portable Generation ID/path identity and is guarded here. Adversarial root or
junction substitution remains a separate hardening finding if that threat model
is approved for Runtime Generation.

Train Confirmation snapshot relative-path serialization is a separate evidence
artifact boundary and is intentionally unchanged. Native Windows 11 Enterprise
source-runtime acceptance remains required after independent audit/merge.

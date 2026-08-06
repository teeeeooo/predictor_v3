record:
  date: 2026-08-06
  topic: windows-model-lifecycle-substitution-safety-correction
  tags: model-lifecycle, windows, filesystem, substitution, containment, recovery
  memory_review: updated
  memory_reason: The audited Windows mutation safety policy now requires native path pinning, not pre/post validation alone.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The independent audit of PR #54 head
`967c8c4d29e8e05a966afb90531f12ba47c5c8f6` invalidated its Windows persisted-state
safety evidence. Validation before a full-path mutation and containment checks
afterward could detect root or parent substitution only after an external lock or
artifact had already been created or written.

# Contract / Behavior Changed

- Every Windows lifecycle mutation now holds native handles without
  `FILE_SHARE_DELETE` for all owned root-to-parent components from validation
  through mutation and post-mutation identity checks. Rename-based substitution
  of any pinned component is rejected by Windows before the mutation target can
  escape the workspace.
- Lock, regular, and exclusive file opens use the same native handle owner with
  `FILE_FLAG_OPEN_REPARSE_POINT`; leaf handles also omit delete sharing while in
  use. Writable durability handles and write-through atomic moves remain intact.
- Candidate and run-evidence directory publication, Active replacement,
  exclusive lifecycle safety publication, rollback/recovery moves, owned-file
  removal, child-directory creation, and writer locking share this mechanism.
- POSIX continues to use its unchanged directory-FD anchoring, no-follow,
  file/directory fsync, rename/link, and writer-lock paths.

# Evidence And Verification

Deterministic macOS-hosted Windows simulations inject root or nested-parent
substitution immediately before lock/exclusive open, Candidate/run rename,
Active replace, rollback rename, and owned-file removal. They assert the complete
external tree remains byte-for-byte unchanged, not merely that an exception is
returned. Native-call simulation separately verifies that directory and file
handles omit `FILE_SHARE_DELETE`, directory handles request backup semantics,
and file/directory handles open reparse points themselves. Nominal Windows,
recovery/fault, lifecycle ownership, closeout, and direct Train persistence
coverage are re-executed at the repaired head. Native Windows remains unavailable.

# Changed Files

The correction remains in the shared Model Lifecycle filesystem/locking boundary,
one native Windows handle helper, direct adversarial simulations, this correction
record/index, and the existing lifecycle Memory entry. Persisted schemas and
application semantics are unchanged.

# Known Risks

Native Windows 11 Enterprise execution is still required as external acceptance
evidence. Deployment Export has a separate publication owner and remains a
conditional follow-up; this correction does not broaden into that owner.

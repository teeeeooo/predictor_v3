record:
  date: 2026-08-06
  topic: windows-model-lifecycle-persistence-compatibility
  tags: model-lifecycle, windows, candidate, active, recovery, durability, filesystem
  memory_review: updated
  memory_reason: Core lifecycle persistence now has an explicit Windows safety and durability policy distinct from POSIX directory-descriptor semantics.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The shared Model Lifecycle filesystem owner assumed POSIX directory descriptors,
`dir_fd` operations, directory `fsync`, and read-only file descriptors for tree
durability. Those primitives are not a valid Windows persistence contract and
blocked Train Candidate, run-evidence, Active, and recovery operations.

# Contract / Behavior Changed

- `LifecycleFilesystem` retains ownership, containment, object-type, and
  device/inode identity policy while selecting one narrow Windows primitive
  adapter.
- Windows uses write-through full-path no-clobber Candidate/rollback rename,
  atomic Active replacement, exclusive artifact publication, and full-path
  removal without opening or syncing directories.
- Windows tree durability opens validated regular files read/write before
  `fsync`; reparse-point objects are rejected and every path mutation rechecks
  parent and published-object identity and resolved workspace containment.
- POSIX retains directory-FD anchoring, `O_NOFOLLOW`, file and directory
  `fsync`, atomic rename/link operations, and all existing recovery behavior.
- The existing Windows `msvcrt` lock backend remains the coordination owner;
  the repaired filesystem now validates the workspace root before that lock can
  create its coordination file.

# Evidence And Verification

Windows-semantics tests reject any directory open, directory `fsync`, `dir_fd`
argument, or read-only file descriptor passed to `fsync`. Under those guards,
they exercise successful immutable Candidate and run-evidence publication,
successful and failed Active replacement, Candidate and Active recovery,
exclusive closeout artifact publication/no-clobber, lock balancing, and root
substitution rejection without external writes. Existing lifecycle, promotion,
recovery, closeout, Train persistence, and POSIX adversarial suites remain the
regression authority. Native Windows execution remains unavailable.

# Changed Files

The source change stays within the shared lifecycle filesystem and locking
boundary, a narrow Windows primitive adapter, direct Windows-semantics tests,
and this record/index/memory update. Persisted schemas and lifecycle application
semantics are unchanged.

# Known Risks

Windows cannot reproduce POSIX containing-directory `fsync` through Python's
ordinary directory descriptor path. The bounded policy therefore relies on
same-filesystem atomic Windows path operations, writable file flushes, and
pre/post identity and containment validation. Native Windows acceptance remains
required. Deployment Export owns separate publication code and is not covered
by this repair.

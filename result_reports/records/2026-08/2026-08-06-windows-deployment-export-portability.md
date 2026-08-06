record:
  date: 2026-08-06
  topic: windows-deployment-export-portability
  tags: deployment-export, windows, durability, atomic-publication, containment
  memory_review: no-change
  memory_reason: Existing memory already identifies Deployment Export as the separate Windows source gate and native Windows as external acceptance evidence.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Deployment Export owns a publication path separate from Model Lifecycle Core.
It opened completed export files read-only before `fsync`, opened directories as
file descriptors for directory `fsync`, and used plain Windows rename without a
write-through durability contract. Its user-selected export parent and private
stage could also be substituted between validation and mutation.

# Contract / Behavior Changed

- Windows export files are synced through writable, no-reparse descriptors.
- Windows does not open or `fsync` export directories. Final no-clobber
  publication uses a write-through Windows directory move.
- The canonical filesystem-anchor-to-export-parent path and the private stage
  path are pinned with native no-delete-sharing handles while they are mutated.
  The final directory must retain the staged directory identity.
- Pre-publication failure removes only private staging. Post-publication
  validation/durability failure removes only the newly published export and
  preserves prior exports.
- POSIX retains read-only file sync, directory sync, and its existing
  `renamex_np`/`renameat2` no-replace publication behavior.

# Evidence And Verification

macOS-hosted Windows simulations reject directory open/sync and read-only file
sync, verify four writable artifact syncs, exercise failure before and after
final publication, and inject export-parent and stage substitution immediately
before mutation while asserting the external directory remains unchanged.
Native-call simulation verifies `MOVEFILE_WRITE_THROUGH` without replacement.
Existing immutable export contents, checksum, no-clobber, structured failure,
Active/Candidate preservation, and Train model-management caller tests remain
the behavior authority. Native Windows execution is unavailable to this Worker.

# Changed Files

The source change remains in the independent Deployment Export publication
owner plus one owner-specific Windows adapter. It reuses only the audited native
handle primitive, not Model Lifecycle Core publication orchestration. Tests and
this record/index complete the source slice; persisted export schemas and caller
contracts are unchanged.

# Known Risks

Native Windows 11 Enterprise source-runtime acceptance remains required after
independent exact-head audit and merge/Close. Reserved filenames, long paths,
packaging, Standard Request, and Predict-to-Calculate remain outside this slice.

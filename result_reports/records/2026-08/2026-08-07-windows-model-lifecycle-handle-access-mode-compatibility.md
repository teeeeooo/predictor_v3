record:
  date: 2026-08-07
  topic: Windows Model Lifecycle handle access-mode compatibility
  tags: model-lifecycle, windows, handles, crt, candidate, active, deployment-export
  memory_review: no-change
  memory_reason: Existing Windows persistence memory already captures the shared handle safety/durability contract and native acceptance resume point.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Native Windows acceptance exposed that the shared Model Lifecycle native-handle
primitive used `os.O_ACCMODE`, which is not available in the affected Windows
Python environment. Candidate, Active, locking/closeout and Deployment Export
therefore shared one platform compatibility failure despite otherwise-correct
Win32 handle semantics.

# Contract / Behavior Changed

The existing access-mode bits are now derived from the portable `O_WRONLY` and
`O_RDWR` flags, with `O_RDONLY == 0` retaining its established meaning. The same
mode is used for Win32 GENERIC access selection and CRT descriptor conversion.
Create/open disposition, no-delete sharing, reparse-point handling, exclusive
creation, CRT ownership transfer and conversion-failure cleanup are unchanged.

# Evidence And Verification

- Starting source reproduced `AttributeError` when a Windows-like `os` surface
  intentionally omitted `O_ACCMODE`.
- Native-handle simulations cover read-only, write-only, read/write, create,
  exclusive-create/no-clobber and CRT-conversion failure ownership.
- Narrow shared Windows persistence/export regressions: `20 passed`.
- Targeted lifecycle/Windows publication suite: `42 passed`.
- Native Windows Candidate publication / Deployment Export: `NOT RUN` /
  `NOT AVAILABLE` from the macOS Worker environment.

# Changed Files

Production changes are limited to the existing shared native-handle primitive.
Tests update the two Windows simulation owners to use test-owned portable access
mode interpretation and add direct native-handle regressions. This record and
`result_reports/REPORT_INDEX.md` preserve the platform defect evidence.

# Known Risks

Native Windows real Train execution through Candidate publication remains the
post-merge acceptance gate. Runtime Generation, Experiment persistence and the
later Headless CLI JSON stdout slice are intentionally unchanged.

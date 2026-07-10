# Design Record Legacy Migration

record:
  date: 2026-07-10
  topic: design record legacy migration
  tags: agent-harness, design-records, legacy
  memory_review: no-change
  memory_reason: active memory's only current design pointer (harness redesign) remains at root and moved records remain indexed

## Reason And Classification

The active design root mixed current governing decisions with historical
implementation evidence. Forty-five records were classified as 15 absorbed,
3 deferred-resume, 8 superseded, and 19 completed.

## Change And Preservation

- Moved all 45 historical records to `docs/designs/legacy/` without changing
  their bodies and added a status/reason/read-when index.
- Kept four current/governing/future-unabsorbed dated records at the root and
  rewrote the root index around active discovery only.
- Updated the approved active inbound references while preserving design assets.
- Historical path literals inside moved bodies remain intentional; the current
  physical path and indexes win.

## Verification

- Root dated-record count is 4 and legacy dated-record count is 45.
- All 45 moved files match their `HEAD` source blob hashes; mismatches: 0.
- Design assets remain present.
- Approved active consumers contain no stale pre-move paths; remaining old-path
  literals are intentional historical evidence.
- `git diff --check`, rename summary review, and
  `py_compile apps/calculator/ui/__init__.py` passed.

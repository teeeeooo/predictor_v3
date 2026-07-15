```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase2-slice2de-rollback-regression-correction
  tags: train-admin, mapping, phase-2, slice-2d, slice-2e, rollback, regression
  memory_review: no-change
  memory_reason: The existing memory already preserves the best-effort mixed-package rollback contract; this correction only strengthens its test evidence.
```

# Change Reason

The mixed existing/new rollback test failed before publishing its first new
target, so it proved restoration of replaced existing files but did not execute
the rollback branch that removes a newly created target.

# Contract / Behavior Changed

Production behavior and public contracts are unchanged. The mixed fixture now
starts with two existing targets, records successful publishes after the real
`os.replace`, proves two existing replacements and one new-target creation, and
then injects failure before the fourth publish.

# Evidence And Verification

- The focused export regression proves three completed target publishes before
  failure and distinguishes existing replacements from new creation: 9 passed.
- Slice 2D+2E focused correction gate: 46 passed; impacted mapping/Train
  regression: 143 passed.
- After rollback, original files are byte-identical, the published new target
  and every unpublished target are absent, and the temporary tree is removed.
- Native macOS interaction was not retried and no PNG is claimed.
- Full suite was not repeated because this correction changes tests and status
  records only; the preceding production correction full-suite result remains
  2064 passed with 2 expected failures.

# Changed Files

- Exchange export rollback regression test.
- Work plan, result index, and this correction record.

# Known Risks

- Rollback remains best-effort if the operating system also blocks backup
  restoration; this test makes no stronger atomicity claim.

record:
  date: 2026-08-07
  topic: Headless JSON stdout encoding compatibility
  tags: experiment, headless, windows, stdout, json, encoding, unicode
  memory_review: no-change
  memory_reason: The durable public stdout transport invariant is explicit in the active headless workflow and current source; no separate long-term memory entry is needed.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The versioned Experiment/headless CLI serialized legitimate Unicode as raw text
and then delegated encoding to inherited `sys.stdout`. Under a cp949-like stream,
valid results could become validation failures and Unicode diagnostics could
fail before any JSON envelope reached the caller.

# Contract / Behavior Changed

The shared headless output owner now emits non-ASCII values through standard
JSON escapes. Parsed `predictor_v3.experiment_output.v1` values are unchanged,
including command, outcome, message, diagnostics, and data. Existing exit
classes, one-result stdout behavior, and Experiment application-service owners
remain unchanged; the internal Train child transport is not part of this diff.

# Evidence And Verification

- Starting source reproduced the defect with `PYTHONIOENCODING=cp949:strict`:
  valid Unicode output returned exit `2` instead of `0`, Unicode run-log output
  returned exit `2`, and a Unicode unreadable-spec diagnostic returned exit `1`
  with zero stdout bytes and `UnicodeEncodeError`.
- Focused locale/output regressions: `5 passed`.
- Stabilized Experiment/headless targeted suite across contract, real run/read,
  agent campaign, and confirmation owners: `61 passed` with existing joblib
  deprecation warnings only.
- Native Windows real headless execution: `NOT RUN` / `NOT AVAILABLE` from the
  macOS Worker environment. Forced-cp949 subprocess tests are regression evidence
  only and are not native Windows acceptance.

# Changed Files

- `apps/train/interfaces/headless/command_contract.py`
- `tests/apps/train/application/test_headless_stdout_encoding.py`
- `docs/workflows/phase5f_headless_experiments.md`
- this record and `result_reports/REPORT_INDEX.md`

# Known Risks

Native Windows acceptance still requires post-merge real headless execution in
the continuous source-runtime acceptance pass. No evidence in this repair
invalidates previously accepted Runtime Generation, Train startup, or Result
Review evidence.

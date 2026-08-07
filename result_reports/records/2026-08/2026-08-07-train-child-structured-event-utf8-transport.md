record:
  date: 2026-08-07
  topic: Train child structured-event UTF-8 transport
  tags: train, windows, process-transport, utf-8, qprocess, subprocess, structured-event
  memory_review: no-change
  memory_reason: The durable transport contract belongs in the architecture owner; merge-dependent Windows resume sequencing remains Close-owner state.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Native Windows real Train exposed a `cp949` encode failure while Core training
sent legitimate Korean/emoji status text through the shared child job. The
producer inherited the locale stream encoding while both process adapters
already consumed the internal wire as UTF-8.

# Contract / Behavior Changed

The shared Train child configures stdin, stdout, and stderr as strict UTF-8
before protocol activity. Structured JSON event meanings, run/generation
identity, progress/result fields, confirmation grants, and natural-language log
content are unchanged. QProcess and subprocess adapters keep their existing
UTF-8 consumer behavior; no duplicate locale policy was added to them.

# Evidence And Verification

- Starting source reproduced `UnicodeEncodeError` with `PYTHONIOENCODING=cp949`
  and the existing package/Korean/emoji training-style log payload.
- Forced-cp949 child/consumer regressions: `5 passed`.
- Existing QProcess cancellation/error/success and confirmation regressions:
  `14 passed`.
- Existing Train lifecycle/Candidate and atomic start-permit regressions:
  `20 passed`.
- Native Windows real Train execution: `NOT RUN` / `NOT AVAILABLE` from the
  macOS Worker environment. Forced-locale tests are regression evidence only.

# Changed Files

- `apps/train/jobs/train_job.py`
- `tests/test_apps_train_process_encoding.py`
- `docs/architecture/pyside6_train_predict_architecture.md`
- this record and `result_reports/REPORT_INDEX.md`

# Known Risks

Native Windows acceptance still requires post-merge real Train execution through
Candidate publication. The versioned Headless CLI stdout owner and Model
Lifecycle Windows-handle/filesystem slice are intentionally unchanged.

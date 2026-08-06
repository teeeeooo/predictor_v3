record:
  date: 2026-08-06
  topic: native-windows-acceptance-onboarding-blocker
  tags: windows, native-acceptance, runtime-generation, result-review, train, onboarding, data-definition, data-mapping
  memory_review: updated
  memory_reason: Native acceptance now has reusable partial PASS evidence and a concrete onboarding blocker/resume point.

# Change Reason

Native Windows 11 Enterprise acceptance directly confirmed repaired runtime and UI
paths, but real Train acceptance cannot proceed through Candidate publication until
the user can prepare the current training-header and local Mapping contracts through
supported product onboarding flows.

# Contract / Behavior Changed

No runtime or source behavior changed in this record. Current execution sequencing
changes: Data Definition / Data Mapping onboarding becomes the next source gate, and
Native Windows acceptance is paused until that prerequisite closes.

Confirmed native evidence:

- previously affected runtime-generation state recovers successfully;
- clean-state Train application startup succeeds; and
- repaired Result Review pinned-table alignment renders correctly.

Full Windows acceptance remains open. Real Train execution through Candidate
publication plus remaining Predict, Experiment, Calculator, and Deployment Export
acceptance are still required.

# Evidence And Verification

The user performed the three checks above on the Native Windows 11 Enterprise
environment after PR #57 Close and reported them successful. This evidence is manual
and environment-specific; reuse requires the same relevant runtime/UI contracts to
remain uninvalidated. No claim is made for Train Candidate publication or the
remaining application acceptance paths.

# Changed Files

Documentation/current-state owners only: WORK_PLAN, project log, active memory, this
record, and REPORT_INDEX.

# Known Risks

- Training header/template and missing-Mapping bootstrap onboarding are not yet
  implemented.
- Company-local mapping values, training data, model quality, and Candidate output
  remain external to repository validation.
- Later source changes may invalidate some already confirmed native evidence and
  require proportional re-check.

# Smoke-loop And Report-exemption Retirement

record:
  date: 2026-07-10
  topic: smoke-loop and report-exemption retirement
  tags: agent-harness, ui-workflow, change-gate
  memory_review: no-change
  memory_reason: existing agent workflow/lifecycle seed entry already captures the conditional-report and gate boundary

## Reason

The standalone UI smoke workflow and legacy mandatory-report exemptions
duplicated active owners after the conditional-record policy became canonical.

## Change

- Merged the focused manual UI smoke fast lane into the UI surface workflow and
  deleted its standalone owner.
- Deleted the commit-message exemption hook and removed the parser
  `ChangeGate` fields `report_exemption` / `read_ledger` plus manifest exemption
  metadata.

## Preserved Behavior

- Preserved `ui_literal_exemption`, manifest `allowed_paths` / `report_path`,
  pre-commit objective checks, and conditional record/index/memory checks.

## Verification

- 31 focused tests passed with `PYTHONPATH=.`.
- `py_compile` passed.
- Structure guard reported only 9 pre-existing hotspot warnings.
- `git diff --check` passed.

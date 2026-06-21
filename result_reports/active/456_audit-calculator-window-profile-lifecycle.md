# 456 Audit Calculator Window/Profile Lifecycle

## Goal

Audit current calculator profile lifecycle composition against active workflow
and window policy before designing a common controller.

## Result

- Compared top-level profile, nested-tab, and detail visibility flows for ISO,
  EN14825, and AHRI.
- Confirmed that measurement, scheduling, shell geometry, and primitive geometry
  already have valid separate owners.
- Classified repeated profile-local construction, trigger delegation, suppression
  wiring, and scroll-reset registration as structural debt.
- Preserved ISO mode predicates, AHRI visibility predicates, and evidence-based
  settle-cycle differences as justified policy inputs.
- Defined the owner candidates and migration/gate questions that task 2 must
  resolve.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.
- `git status --short` — only task 1 files staged before commit.

## Changed Files

- `docs/designs/2026-06-21-calculator-window-profile-lifecycle-audit.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/456_audit-calculator-window-profile-lifecycle.md`

## Read Ledger

- `AGENT_TASK_ROUTER.md`: architecture triage, UI gate, report route; reason:
  audit boundary and reporting.
- `UI_SURFACE_WORKFLOW.md`: window/dynamic gate; reason: compliance baseline.
- `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`: profile, detail, nested, stable
  container ranges; reason: lifecycle policy baseline.
- `AGENT_CHANGE_GATES.md`: pre-write/report ranges; reason: docs/report gate.
- calculator app, three profile tabs, measurement, shell, scheduler, geometry:
  lifecycle symbols and surrounding owner ranges only; reason: compare assembly.
- broad read: none
- repeated read: none

## Next Action

Profile visible-content lifecycle controller design.

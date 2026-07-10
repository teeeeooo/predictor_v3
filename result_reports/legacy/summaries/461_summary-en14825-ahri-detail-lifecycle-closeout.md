# 461 Summary: EN14825/AHRI Detail And Lifecycle Closeout

## Covered Reports

449–461:

- EN14825 SCOP and SEER detail implementation and design sync;
- shared bin-detail scroll affordance;
- AHRI HSPF2 and SEER2 detail implementation;
- EN14825 negative and undermeasured profile-switch corrections;
- profile lifecycle audit, controller design, three-profile migration, and
  lifecycle ownership hard gate.

## Completed Work

- EN14825 SCOP/SEER and AHRI HSPF2/SEER2 preserve existing core bin diagnostics
  through additive adapter/model boundaries and render profile-owned normalized
  rows through `BinDetailPanel`.
- All four detail surfaces provide explicit input-waiting/error/no-data states,
  stale-row invalidation, table/graph/copy/CSV behavior, and visible-content
  refit callbacks without changing core equations or public result keys.
- The common bin table retains vertical scrolling and an always-visible
  horizontal scrollbar for wide schemas.
- Negative geometry underflow is guarded in measurement and geometry policy;
  positive-but-transient top-level undermeasurement is corrected by a settled
  parent-selection refit.
- `ProfileVisibleContentLifecycleController` now owns scheduler, measurement,
  content-hugging shell/form, suppression, named triggers, fit, and scroll-reset
  composition for ISO16358, EN14825, and AHRI210240.
- Profile tabs retain widget composition, active predicates, and injected
  settle-cycle policy. A structure gate prevents direct primitive assembly from
  returning to production `tabs/*.py`.

## Durable Decisions

- Detail rows are UI schema/formatter outputs; raw core dictionaries never flow
  directly into common tables.
- Detail visibility, nested-tab changes, and parent profile selection use named
  controller triggers rather than local geometry calls.
- Profile-specific behavior is configuration: EN parent selection uses two
  cycles; AHRI inner metrics use a visible-only two-cycle trigger; ISO nested
  measurement is active only in Hong Kong mode.
- Existing lifecycle primitives remain separate owners and are composed, not
  merged into the controller.
- Sample performance values were intentionally retained through this arc; their
  removal now proceeds under the recorded empty-state policy.

## Validation Summary

Each implementation slice passed its focused adapter/detail/lifecycle suites,
the structure guard, code-map judgment, diff check, and staged change gate. GUI
timing and wide-table visual confirmation remain appropriate manual smoke, but
no active source blocker remains for the next empty-state slice.

## Archived Reports

- `449_implement-en14825-scop-detail-view.md`
- `450_sync-en14825-ahri-detail-design-record.md`
- `451_implement-en14825-seer-detail-view.md`
- `452_add-bin-detail-scroll-affordance.md`
- `453_implement-ahri-hspf2-detail-view.md`
- `454_harden-en14825-profile-switch-sizing.md`
- `455_settle-top-level-profile-switch-refit.md`
- `456_audit-calculator-window-profile-lifecycle.md`
- `457_design-profile-visible-content-lifecycle-controller.md`
- `458_implement-lifecycle-controller-en14825-migration.md`
- `459_migrate-ahri-iso-profile-lifecycle.md`
- `460_enforce-profile-lifecycle-owner-gate.md`
- `461_implement-ahri-seer2-detail-view.md`

## Next Action

Calculator sample data removal and empty-state implementation using
`docs/designs/2026-06-21-calculator-sample-data-empty-state-policy.md`.

# 458 Implement Lifecycle Controller And EN14825 Migration

## Goal

Implement the approved common visible-content lifecycle controller foundation
and migrate EN14825 without changing its external or detail lifecycle behavior.

## Result

- Added the feature-owned `apps/calculator/ui/lifecycle/` package.
- The controller composes existing measurement, scheduler, shell/form, snapshot,
  suppression, fit, and scroll-reset owners without copying their policy logic.
- Named parent, nested-tab, and detail triggers apply configured settle cycles.
- EN14825 delegates all lifecycle assembly and keeps
  `preferred_initial_size()`, `fit_toplevel_to_current_content_once()`, and
  `on_parent_tab_selected()` compatible.
- Temporary read-only private aliases preserve existing diagnostics until the
  affected tests can migrate with the remaining profiles.
- Initial SCOP construction invokes its detail callback, so controller creation
  was placed immediately after nested notebook construction and before section
  composition. The failed first test run caught and fixed this ordering contract.

## Verification

- Controller-focused tests — 7 passed.
- EN14825 profile-switch plus SEER/SCOP detail tests — 13 passed.
- `python3 -B tools/check_code_structure.py` — no errors; two expected new
  package-registry warnings plus four existing soft warnings.
- Package-registry registration is deferred to task 5 because task 3 forbids
  tool changes and task 5 explicitly owns lifecycle enforcement.
- Code-map check was stale after source/package changes; regenerated once.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Structure Triage

- `lifecycle/controller.py` has one cohesive responsibility: compose existing
  visible-content lifecycle primitives and expose named triggers.
- It does not own view construction, geometry math, measurement arithmetic, or
  domain behavior and remains below source soft limits.
- The package-registry warning is not an owner-boundary defect; registration is
  queued in the already-approved hard-gate task 5.

## Changed Files

- `apps/calculator/ui/lifecycle/__init__.py`
- `apps/calculator/ui/lifecycle/controller.py`
- `apps/calculator/ui/tabs/en14825_tab.py`
- `tests/test_ui_tk_profile_lifecycle_controller.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/458_implement-lifecycle-controller-en14825-migration.md`

## Change Gate

```yaml
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- controller design and lifecycle audit: constructor/public policy and migration
  boundary; reason: approved implementation contract.
- EN14825 tab lifecycle ranges and focused private-field test references; reason:
  behavior-preserving delegation and compatibility.
- existing measurement, scheduler, shell public constructors/methods; reason:
  composition without policy duplication.
- structure package registry range: warning owner only; reason: task 5 handoff.
- broad read: none
- repeated read: EN14825 constructor after failed test exposed immediate SCOP
  callback ordering.

## Next Action

AHRI210240 and ISO16358 lifecycle migration.

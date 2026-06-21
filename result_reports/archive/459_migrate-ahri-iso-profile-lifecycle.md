# 459 Migrate AHRI And ISO Profile Lifecycle

## Goal

Migrate AHRI210240 and ISO16358 to the common lifecycle controller while
preserving profile predicates, settle policy, detail behavior, and EN regression.

## Result

- AHRI now injects its outer-visible predicate and two-cycle nested metric policy
  into the controller; HSPF2 detail uses the named detail trigger.
- ISO now injects its Hong Kong-only nested measurement predicate and delegates
  preferred size, immediate fit, detail visibility, nested metric changes, and
  explicit mode/region refits.
- Both tabs retain read-only measurement/scheduler aliases for existing focused
  diagnostics, but no longer construct lifecycle primitives or register shell
  content directly.
- EN migration behavior remains intact.
- Focused ISO callback tests were aligned with the current section-owned
  `_on_detail_visibility_changed` name, and one stale Hong Kong HSPF result test
  now asserts the current detail-summary owner instead of a removed ResultPanel
  getter.

## Verification

- AHRI window/HSPF2 detail/sizing diagnostics — 10 passed.
- ISO lifecycle and Hong Kong HSPF detail — 21 passed.
- ISO scheduler/profile/detail focused selection — 11 passed.
- EN14825 profile-switch regression — 4 passed.
- `python3 -B tools/check_code_structure.py` — no errors; pending lifecycle
  package registration and existing soft warnings only.
- Code-map check was stale after profile source changes; regenerated once.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Policy Split

- Common: primitive construction, measurement suppression, shell registration,
  fit, scroll reset, request coalescing, named detail/nested triggers.
- AHRI-specific input: outer visibility predicate and two-cycle metric settling.
- ISO-specific input: Hong Kong-mode predicate and explicit two-cycle first mode
  entry; ordinary nested/detail events remain one cycle.
- EN-specific input: two-cycle parent selection.

## Changed Files

- `apps/calculator/ui/tabs/ahri210240_tab.py`
- `apps/calculator/ui/tabs/iso16358_tab.py`
- `tests/test_ui_tk_window_lifecycle_repair.py`
- `tests/test_ui_tk_hong_kong_hspf_detail.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/459_migrate-ahri-iso-profile-lifecycle.md`

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- lifecycle design profile matrix; reason: approved injected policy.
- AHRI and ISO lifecycle construction/event ranges; reason: bounded migration.
- focused private scheduler/measurement tests and section callback owners; reason:
  compatibility and current contract alignment.
- broad read: none
- repeated read: ISO/Hong Kong focused failures exposed stale test owner names,
  then only matching section/result ranges were checked.

## Next Action

Lifecycle hard gate implementation.

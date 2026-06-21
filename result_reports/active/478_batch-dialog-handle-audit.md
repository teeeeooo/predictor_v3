# 478 Batch Dialog Handle Audit

## Goal

Decide whether repeated batch dialog open/focus/snapshot/close state can share a
thin handle without changing constructors, snapshots, or focus behavior.

## Evidence

- Six sections repeat the same fields and lifecycle: current dialog, latest
  snapshot, focus existing, construct one dialog, retain non-`None` snapshot,
  clear reference, and close on section disposal.
- AHRI HSPF2 already isolates this responsibility in
  `AhriHspf2BatchAccess`, demonstrating that section-level delegation reduces
  pressure on a large main section.
- Constructors differ: Hong Kong adds a region label; snapshot types include
  lists and typed dataclasses; HSPF2 always stores the close snapshot while
  other sections ignore `None`.
- Focused persistence/lifecycle suites across all seven profiles: 50 tests
  passed.

## Decision

**Accept a generic state handle only as a separately designed implementation
slice.** The handle may own `dialog`, `snapshot`, `open_or_focus(factory)`,
`clear(snapshot)`, and `dispose()`. A factory closure supplied by each profile
must own constructor differences. Snapshot `None` policy must remain an
explicit profile callback/policy rather than being silently standardized.

Do not make the handle own buttons, layout rows, dialog constructors, or tab
lifecycle. `AhriHspf2BatchAccess` should remain the HSPF2 button/composition
owner and may delegate only its state mechanics internally.

## Suggested Design Gate for Implementation

- Define small Dialog protocol: `focus()`, `close()`, and live-state contract.
- Decide whether liveness uses `dialog is not None` or `window.winfo_exists()`;
  guard tests must cover externally destroyed windows before standardizing it.
- Preserve close-callback ordering so `dispose()` cannot resurrect or retain a
  stale dialog.
- Allow sections/one helper/focused persistence tests only; forbid tab changes,
  constructor rewrites, snapshot schema changes, and lifecycle primitives in
  tabs.

## Changed Files

- `result_reports/active/478_batch-dialog-handle-audit.md`

## Architecture Judgment

The candidate is a narrow controller/state handle and fits MVC/SoC if factory
and snapshot policy stay profile-owned. A generic dialog manager that also
builds buttons/layout would conflate view composition and lifecycle, so it is
rejected. The unresolved live-window policy warrants a design gate rather than
immediate refactoring.

## Known Risks

- `winfo_exists()` behavior differs from HSPF2's current reference-only check.
- Close callbacks during destruction can be re-entrant; implementation needs
  explicit tests before replacing proven local code.
- Implementation is not authorized in this audit commit.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- section `_open_batch_dialog`, `_clear_batch_dialog`, and disposal symbol
  ranges across seven profiles; reason: compare exact lifecycle contract.
- HSPF2 batch access: complete small file; reason: evaluate existing delegated
  owner as reference evidence.
- dialog wrappers: constructor signatures from targeted ranges; reason:
  identify factory and snapshot differences.
- focused persistence tests: selected lifecycle cases; reason: behavior
  evidence.
- broad read: none.
- repeated read: none.

## Commit / Push

Audit-only commit; published with the complete arc.

## Next Suggested Action

Audit detail-toggle ownership against the visible-content lifecycle controller.

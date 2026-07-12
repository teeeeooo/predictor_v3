```yaml
record:
  date: 2026-07-12
  topic: calculator-scop-visible-export-correction
  tags: calculator, tkinter, scop, visible-result, copy, csv, correction
  memory_review: updated
  memory_reason: SCOP visible climate surfaces, not the compatibility ResultPanel, are the durable Single result export owner.
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
```

# Change Reason

SCOP's visible Copy/CSV buttons were wired to a hidden compatibility
`ResultPanel`, so invalid, warning, pending, and mixed climate states could
disagree with the cards users actually saw. The prior small action presenter
package also produced two new structure-registry warnings.

# Contract / Behavior Changed

Each `ScopResultSurface` now exposes an immutable snapshot of its current
visible headers, rows, and status. `En14825ScopSection` filters those snapshots
by active climate in Average/Warmer/Colder order and owns sectioned Copy/CSV
composition. Visible values and status are included for calculated climates;
status-only climates preserve their actual invalid, warning, or pending text.
Inactive climates and detail/bin rows are excluded, and surface transitions
clear stale values before export.

The generic action helper still owns only button/callback dispatch, but its
single presenter module is flattened to `apps/calculator/ui/result_actions.py`.
The unnecessary package directory is removed without changing imports or other
profile result owners.

# Evidence And Verification

- 151 focused SCOP, ResultPanel, ISO, Brazil, inventory, and geometry regression tests passed before the final transition assertion refinement.
- The final full Tk Calculator UI selection passed 666 tests in suite order.
- Focused tests cover complete, invalid, warning, pending, mixed active climates, active/inactive transitions, stale-value removal, CSV filename/cancel, and detail exclusion.
- Python compilation and whitespace checks passed.
- Structure guard reports only the same 10 pre-existing hotspot/class-count warnings; the two `result_actions` package-registry warnings are gone.

# Changed Files

- SCOP compact result surface snapshot and section-owned Copy/CSV composition
- flattened shared `result_actions.py` presenter
- focused SCOP visible-state/export tests
- project log, memory seed, and report index

# Known Risks

The EN14825 SCOP section remains an existing hotspot; this correction adds only
bounded export composition and does not split or move lifecycle/calculation
responsibility. Automated clipboard/CSV and state-transition tests passed, but
the user should perform the requested final visible mixed-climate GUI and file
dialog review before merge.

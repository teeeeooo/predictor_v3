```yaml
record:
  date: 2026-09-02
  topic: ahri-m-table-interaction-parity
  tags: calculator, ahri210240, appendix-m, ui, table, clipboard, interaction
  memory_review: no-change
  memory_reason: The durable M/M1 calculator ownership split is unchanged; this correction only reconnects M UI tables to the already-shared interaction owner.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Post-implementation review found AHRI Appendix M main `MetricInputTable` surfaces using native Tk Entry interaction instead of the Excel-like table interaction already used by M1. The M HSPF batch common-input table had the same gap.

# Contract / Behavior Changed

- M SEER main numeric/input tables now use the shared `TkTableController` already used by M1.
- M HSPF main numeric/heating tables now use the same controller, preserving drag range selection, TSV copy/paste, grouped undo, type-to-replace, and keyboard navigation.
- HSPF optional-point, Demand Defrost, and Automatic Cutout presentation changes refresh controller bindings after Entry/read-only Label swaps.
- The M HSPF batch common-input `MetricInputTable` uses the same controller and refresh contract. The existing batch case matrix controller is unchanged.

# Evidence And Verification

- Focused M UI interaction regression verifies SEER 2×5 TSV paste and copy through the shared controller and confirms the pasted golden still calculates to published SEER `18.05`.
- HSPF regression verifies disabled H12/H22 cells reject paste, H12 accepts paste after enablement, Demand Defrost timing inputs reject paste while read-only and accept it after enablement, and the newly visible Entry retains drag/paste bindings after controller refresh.
- HSPF batch common-input regression verifies the same binding refresh and controller-driven Defrost Test/Max paste behavior.
- AHRI-filtered suite passes with 208 tests; focused table-controller plus M UI tests pass with 14 tests; structure check and `git diff --check` pass.

# Changed Files

- `apps/calculator/ui/ahri_m/seer_section.py`
- `apps/calculator/ui/ahri_m/hspf_section.py`
- `apps/calculator/ui/ahri_m/batch_sections.py`
- Focused Appendix M UI tests and active design interaction-parity amendment.

# Known Risks

- Selection remains intentionally scoped to one physical `MetricInputTable` at a time, matching the current M1 controller model; this change does not create cross-table drag or paste semantics.
- No calculator formula, profile, public capability, M1 calculation owner, or batch case-matrix interaction behavior changes in this correction.

```yaml
record:
  date: 2026-07-12
  topic: calculator-table-slice3
  tags: calculator, tkinter, compact-result, single-surface, migration
  memory_review: no-change
  memory_reason: The existing Calculator table-family memory already requires simple single matrices and fixed results to adopt the shared families progressively.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Approved Slice 3 required the remaining simple single-profile tables to adopt
the shared visual foundation before batch and complex EN14825 migration.

# Contract / Behavior Changed

Hong Kong, SASO T3, Korea, and AHRI single input matrices now use the shared
flat grid policy without replacing their models or controllers. The SASO fixed
comparison result migrated from Treeview to `CompactResultGrid`. The Korea
midpoint guide migrated to the same compact family while retaining its
section-local address-based read seam.

# Evidence And Verification

- 94 focused single-profile, controller, auto-calc, result, and refit tests passed.
- Targeted Python compilation and whitespace checks passed.
- Structure guard completed with only unchanged legacy warnings.
- SASO headers/rows/status/copy and Korea midpoint values remain guarded.

# Changed Files

- simple Hong Kong, SASO T3, Korea, and AHRI section views
- SASO result and Korea midpoint guide presenters
- focused single-profile UI tests
- `docs/WORK_PLAN.md`

# Known Risks

No manual platform visual smoke was required. Batch, detail Treeview, Brazil
input, and EN14825 surfaces remain intentionally unmigrated for later slices.

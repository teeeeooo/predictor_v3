# 475 Profile-Specific UI Token Exceptions

## Goal

Close the legacy UI literal cleanup arc by classifying every remaining audited
presentation value without forcing unsupported cross-profile commonization.

## Results

- Added a final exception/exclusion ledger with owner, reason, and revisit
  trigger for every remaining literal family.
- Formalized Hong Kong batch schema widths; ISO label selectors; EN14825
  common/SCOP vocabulary widths; hidden result buffers; ResultPanel fallback;
  graph geometry; viewport state; and composition-local spacing.
- Explicitly stated that grandfathered values cannot be copied into new staged
  code without a semantic owner or approved exemption.
- Marked all five cleanup slices complete and moved `WORK_PLAN` to the
  audit-only structure arc.
- No production or test source changed in this slice.

## Verification

- Focused ISO, Hong Kong, SASO, and EN14825 SCOP profile suites: 83 tests passed
  as behavior evidence for the exception owners.
- Structure guard passed hard rules with existing hotspot/freshness warnings.
- Code-map check was run and judged `no-change` for this docs-only slice.
- Final inventory delta and diff checks passed; cached gate recorded at commit
  closeout.

## Changed Files

- `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/475_profile-specific-ui-token-exceptions.md`

## Architecture Judgment

The ledger applies the same MVC/SoC boundary as the implementation slices:
common visual policy belongs to tokens, profile vocabulary/schema stays with
the profile, and runtime allocation stays with the view/geometry owner. A
future abstraction requires a second semantic consumer, not merely a repeated
number. This is intentionally less machinery than per-profile token modules
created only to hide single-use literals.

## Known Risks

- The inventory counts retain their original baseline evidence; the final
  ledger, not those historical counts, is the current disposition.
- Gate coverage remains pattern-focused. Generic spacing and width values rely
  on review plus this ledger rather than an all-numeric linter.
- Active report cleanup is explicitly out of scope and remains pending.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: no-change
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- complete inventory document: explicit full-file inventory closure; reason:
  ensure every prior category receives a final disposition.
- production UI presentation pattern search: owner matches only; reason:
  enumerate remaining grandfathered values without full-file reads.
- focused owner ranges for EN SCOP, EN tab, result buffers, and graph: reason:
  distinguish visible profile policy from runtime/hidden state.
- focused profile tests: matched construction/result ranges; reason: select
  behavior evidence without changing expected output.
- broad read: inventory document only (explicit full inventory requirement).
- repeated read: none.

## Commit / Push

This docs/audit slice is committed independently and pushed once with the
complete arc.

## Next Suggested Action

Audit the detail formatting helper candidate without changing production code.

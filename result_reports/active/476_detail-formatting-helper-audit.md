# 476 Detail Formatting Helper Audit

## Goal

Decide whether repeated detail `_number` / `_text` helpers should share an
owner while preserving profile-specific field mapping and rounding policy.

## Evidence

- EN14825 SEER, EN14825 SCOP, AHRI SEER2, and AHRI HSPF2 each define byte-for-
  byte equivalent numeric and text coercion behavior.
- All four numeric helpers map `None`, type errors, and value errors to blank;
  valid values use caller-provided fixed precision.
- Field keys, output keys, source labels, units, and precision selection differ
  by profile and remain inside each formatter.
- Focused detail suites: 20 tests passed.

## Decision

**Candidate accepted for a later small implementation slice.** A pure helper
module may own only `optional_fixed_number(value, precision)` and
`optional_text(value)`. Profile formatters must retain their explicit mapping
dictionaries/comprehensions and precision at each field call.

Do not introduce a generic schema-driven row transformer: it would hide the
important core-key to UI-key boundary, couple unrelated detail schemas, and add
more abstraction than the duplicated 12-line coercion policy warrants.

## Suggested Implementation Boundary

- Allow: one small pure detail-formatting helper, four formatter imports/calls,
  focused formatter tests, report, and code map.
- Forbid: schema/payload/rounding changes, field registry generation,
  `BinDetailPanel` changes, or section lifecycle changes.
- Acceptance: invalid/`None`/precision behavior remains identical and all
  profile field maps stay visibly local.

## Changed Files

- `result_reports/active/476_detail-formatting-helper-audit.md`

## Architecture Judgment

This boundary improves SoC by sharing coercion policy while keeping adapter-
like profile mapping explicit. It is extensible for another detail formatter
without making the panel or schema aware of core result keys. The rejected
generic transformer would be overengineering.

## Known Risks

- Helper naming must not imply domain-unit formatting; it handles display
  coercion only.
- Implementation is not authorized by this audit commit.
- Active report cleanup remains outside this arc.

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

- four detail formatter files: complete small files; reason: compare helper
  behavior and profile mapping boundaries.
- four focused detail test files: test names and formatter assertions; reason:
  confirm invalid/rounding behavior evidence.
- `BinDetailPanel`: not needed; formatter ownership was clear after symbol
  comparison.
- broad read: none.
- repeated read: none.

## Commit / Push

Audit-only commit; published with the complete arc.

## Next Suggested Action

Audit matrix calculation summary/controller duplication before choosing the
first post-audit implementation slice.

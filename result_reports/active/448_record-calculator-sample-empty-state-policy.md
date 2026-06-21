# 448 Record Calculator Sample and Empty-State Policy

## Goal

Inventory calculator launch defaults, define the performance-empty policy, and
record EN14825/AHRI detail views as a prerequisite to sample removal.

## Scope

- Audit main profile section initialization and explicit mock/default owners.
- Classify option/standard defaults versus product performance demo values.
- Add/index a design policy, update execution/milestone docs, and retire report
  447 after its next action is consumed.

## Inventory Result

- Keep: EN14825 design-condition/options and neutral ancillary powers; AHRI
  Type/Region/optional-point/numeric conditions; SASO optional 35 Min state.
- Remove later: EN14825 declared/tested performance and design capacity, AHRI
  HSPF2 A2/heating-point DEV samples, ISO/ISEER and Hong Kong full/half samples,
  Hong Kong declared capacity, and SASO capacity/power defaults.
- AHRI SEER2 already launches without product performance sample values.

## Policy and Dependency

- New profiles should launch with blank product performance inputs and an
  input-waiting result, while valid option/standard defaults remain selected.
- Hong Kong CSPF/HSPF provide the reference detail-toggle, `BinDetailPanel`,
  trace status/rows, graph/table, and CSV ownership pattern.
- EN14825 SEER/SCOP and AHRI SEER2/HSPF2 lack those detail surfaces. Their detail
  design and implementation must precede sample removal.

## Changed Files

- `docs/designs/2026-06-21-calculator-sample-data-empty-state-policy.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `project_log.md`
- `result_reports/archive/447_formalize-ui-magic-literal-legacy-inventory.md`
- `result_reports/active/448_record-calculator-sample-empty-state-policy.md`

## Lifecycle Decision

Report 447 no longer owns the next decision after this policy record and is
archived. Report 448 remains active as the current audit/design evidence.

## Verification

- Profile initialization and detail-owner inventory: checked with scoped `rg`
  and matching initialization ranges.
- `git diff --check`: passed.
- `python3 -B tools/check_agent_change_gate.py --cached`: passed.
- Code/test suites are intentionally skipped because no production or expected
  behavior changes in this audit slice.

## Known Risks

- Detail data availability and public-result boundaries for EN14825/AHRI remain
  unresolved until the next design slice; this record does not invent schemas.
- Sample values remain in production UI until later explicitly approved removal
  slices.

## Commit / Push

Final publication SHA evidence is reported in the terminal result to avoid a
self-referential report update loop.

## Next Action

EN14825/AHRI detail view design.

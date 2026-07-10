# 447 Formalize UI Magic Literal Legacy Inventory

## Goal

Formalize the grandfathered production UI literal inventory, semantic token
taxonomy, and bounded cleanup sequence without changing production behavior.

## Scope

- Audit presentation literals under `apps/calculator/ui/` through scoped search.
- Separate domain/runtime numbers from shared and profile-local UI candidates.
- Add and index an active-reference design/audit record.
- Advance the work plan and retire completed lifecycle report 446.

## Audit Result

- High-confidence grandfathered groups: 16 raw row/data character widths, seven
  profile minimum-size pairs, and seven legacy batch `width_chars` declarations.
- Broad review groups: 171 spacing assignments, 39 mixed generic widths, and
  nine mixed height assignments.
- Color/font state: no hex color outside the shared owner, one named-color
  exception, and no raw font tuple outside token ownership.
- No fixed numeric geometry call exists in the scanned production UI.
- Domain/regulation/calculation values and runtime allocation sentinels are
  explicitly excluded from mechanical token migration.

## Token and Cleanup Decision

- Token promotion requires a shared semantic role, unit, font/padding
  assumptions, and resize behavior; repeated numeric equality is insufficient.
- Common table, BatchMatrix, dialog/window, input/control, color/font/spacing,
  and profile-specific families are defined.
- Cleanup is split into five slices: dialog minima, common controls, main
  table/results, color/spacing, then profile-specific exceptions.

## Changed Files

- `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `result_reports/archive/446_close-ahri-lifecycle-and-clean-active-reports.md`
- `result_reports/active/447_formalize-ui-magic-literal-legacy-inventory.md`

## Lifecycle Decision

Report 446 no longer owns a current blocker or next decision after this audit
began, so it is archived. Report 447 remains active as the current audit record.

## Verification

- Inventory pattern counts and hotspot ownership: checked with scoped `rg`.
- `git diff --check`: passed.
- `python3 -B tools/check_agent_change_gate.py --cached`: passed.
- Code/test suites are intentionally skipped because production code and test
  expectations are unchanged.

## Known Risks

- Generic width/height and spacing counts contain runtime/layout-state matches;
  each implementation slice must reclassify its exact target before editing.
- This inventory does not authorize an all-numeric linter or bulk replacement.

## Commit / Push

Final publication SHA evidence is reported in the terminal result to avoid a
self-referential report update loop.

## Next Action

Calculator DEV/sample data inventory and empty-state policy.

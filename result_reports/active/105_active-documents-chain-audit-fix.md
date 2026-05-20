# 105 — Active Documents Chain Audit Fix

## Goal

Update `ACTIVE_DOCUMENTS.md` according to the AGENTS.md-started
inbound/outbound chain audit.

## Scope

- Add the missing active design record for calculator horizontal table
  input UI and unit boundary.
- Remove the stale active outbound link from the ISO remaining-work
  design record to missing `iso_separation_result.md`.

## Changed Files

- `ACTIVE_DOCUMENTS.md`
- `result_reports/active/105_active-documents-chain-audit-fix.md`

## Verification

- Re-ran an active inventory path check across root Markdown,
  non-archive `docs/**/*.md`, and
  `data/region_configs/REGION_CONFIG_RULES.md`; no unlisted active
  Markdown paths were reported.
- Confirmed `ACTIVE_DOCUMENTS.md` no longer references
  `iso_separation_result.md`.
- Confirmed the new row for
  `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
  is present.

## Known Risks

- This was metadata-only documentation sync. The design document body
  still contains historical context references as authored; only the
  active owner inventory chain was corrected.
- No `project_log.md` update was made because this did not introduce a
  new architecture/process decision; it corrected stale inventory
  metadata.

## Commit / Push

- Not committed or pushed in this turn.

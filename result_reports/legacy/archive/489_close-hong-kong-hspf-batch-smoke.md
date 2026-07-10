# 489 Close Hong Kong HSPF Batch Smoke

## Goal

Record completed manual smoke for the Hong Kong HSPF batch dialog and perform a
final audit of the recent calculator helper/batch/detail/token/button cleanup.

## Manual Smoke

Closed. The user confirmed:

- Hong Kong HSPF screen shows the `일괄 입력` button.
- The button opens the Hong Kong HSPF batch dialog.
- `7 Full` / `7 Half` capacity and power cells are editable.
- A sample row displays `HSPF`, `HSTL`, and `HSEC` results.
- Closing and reopening the dialog preserves the snapshot.

## Final Audit

- Batch open button text is unified through `BATCH_INPUT_BUTTON_TEXT = "일괄 입력"`.
- Dialog titles remain profile-specific, including `HSPF Batch (Hong Kong)`.
- No production section `_detail_visible` state remains.
- Hong Kong HSPF batch reuses `BatchMatrixCalculationController`.
- Hong Kong HSPF section reuses `BatchDialogHandle`.
- No new calculator blocker was found.

## Hong Kong HSPF Duplicate-Line Check

No duplicate found in the current `recalculate_now()` empty-state condition.
Checked `apps/calculator/ui/sections/hong_kong_hspf_section.py` lines 186-194:
the condition contains one generator expression over
`self.input_table.get_text_values().values()`.

## Changed Files

- `docs/WORK_PLAN.md`
- `result_reports/active/489_close-hong-kong-hspf-batch-smoke.md`

## Verification

- `git status --short` — checked before docs update.
- `git diff --stat` — run at closeout.
- `git diff --check` — run at closeout.
- `python3 -B tools/check_agent_change_gate.py --cached` — run at closeout.

Skipped:

- pytest: docs/audit closeout only.
- code map regeneration: no source structure change.
- structure guard: docs-only closeout.

## Excluded Scope

- No production code, tests, tools, calculator logic, schema/public API,
  fixture/golden, report lifecycle cleanup, main merge, or unrelated docs
  cleanup changed.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  reuse_commonization: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `docs/WORK_PLAN.md` current slice/next actions, reason: update closeout and
  next action.
- Hong Kong HSPF `recalculate_now()` empty-state lines, reason: confirm
  duplicate-line status.
- targeted `rg` checks for batch button text, `_detail_visible`,
  `BatchMatrixCalculationController`, and `BatchDialogHandle`, reason: final
  audit only.
- broad read: none.
- repeated read: none.

## Next Action

Report lifecycle cleanup.

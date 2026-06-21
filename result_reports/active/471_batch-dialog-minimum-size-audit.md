# 471 Batch Dialog Minimum Size Audit

## Goal

Remove profile-specific batch-dialog minimum sizes that duplicate natural
content fitting, while retaining one semantic usability safety floor.

## Audit Evidence

The seven adapters were instantiated under the same Tk environment. Requested
or preferred content widths already owned initial width (790–1409 px in the
audit), while the former profile floors ranged from 920–1180 px. Preferred
content height already owned the table/action content; former 360–420 px
profile heights had no profile-specific invariant.

## Results

- Replaced seven unrelated literal pairs with
  `BATCH_DIALOG_SAFETY_MIN_SIZE` at the shared token owner.
- The common floor protects basic window usability only. Natural requested and
  preferred content sizes continue to determine initial geometry.
- No shell arithmetic, lifecycle, horizontal scrolling, point/result width,
  profile layout, or data contract changed.
- Updated the inventory from an open audit item to a resolved owner decision.

## Verification

- Focused shell, content sizing, and all seven dialog profile suites: 58 tests
  passed.
- A new relation test confirms every adapter uses the shared shell-role floor.
- Structure guard passed hard rules with existing soft warnings.
- Code map was stale from earlier commits and regenerated once.
- Diff check passed; cached staged gate recorded at commit closeout.

## Changed Files

- `apps/calculator/ui/layout_constants.py`
- seven adapters under `apps/calculator/ui/batch_dialogs/profiles/`
- `tests/test_ui_tk_batch_dialog_content_sizing.py`
- `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/471_batch-dialog-minimum-size-audit.md`

## Architecture Judgment

Minimum size is a shell usability policy, not profile calculation or schema
state. A single semantic safety floor removes accidental profile coupling while
leaving content fitting as the size owner. This is smaller and more extensible
than adding per-profile geometry abstractions or changing the shell protocol.

## Known Risks

- Platform font metrics can change requested size; relation tests intentionally
  avoid exact initial pixel assertions.
- Active reports now exceed the normal review threshold. Cleanup is explicitly
  outside this arc, so no reports were archived.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- seven adapter `min_size` properties and import ranges: targeted ranges;
  reason: compare literal ownership without reading profile calculations.
- batch dialog shell geometry method: lines 1-102; reason: establish natural
  fitting and minimum-size interaction.
- content-sizing and shell tests: focused ranges; reason: preserve relation
  contracts.
- legacy inventory batch/dialog sections: targeted headings; reason: close the
  recorded audit item.
- broad read: none.
- repeated read: none.

## Commit / Push

This slice is committed independently and pushed once with the complete arc.

## Next Suggested Action

Name repeated common input and selector widths by semantic control role.

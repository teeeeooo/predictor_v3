# Arc 9.2 Legacy UI Harvest Closeout

## Goal

Close Arc 9.2 as a docs-only correction before Arc 9.5 visual parity work:
move project-specific legacy UI harvest evidence out of portable UI/UX owner
docs, recover missing legacy behavior details from Git history, and route the
new design reference through active project docs.

## Inspected Legacy Ref

- `f8adf7075563838dc8217833b46242ad618fc3ae`

## Inspected Legacy Files

- `ui/base_model.py`
- `ui/base_view.py`
- `ui/spreadsheet_table.py`
- `ui/predict_window.py`
- `ui/train_window.py`
- `ui/theme.py`

## Moved Harvest Document

- From: `docs/ui_ux/06_PYSIDE6_VISUAL_AND_TABLE_PARITY_HARVEST.md`
- To: `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`

The moved document is now a project-specific design/harvest reference for Arc
9.5, not a portable UI/UX owner contract.

## Added Detailed Checklist Summary

- Predict table visual/interaction parity.
- Spreadsheet interaction parity.
- Mapping/autofill parity.
- Row-to-ML/result parity.
- Predict surface visual hierarchy.
- Train admin visual/function inventory.
- Visual token adoption using `ui_common.visual_tokens`.
- Deferred item split across Arc 9.5, Arc 10, Arc 11, and later.

## Updated Routing Docs

- `docs/ui_ux/README.md`
- `docs/designs/README.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`

## Excluded Scope

- No production code changes.
- No `apps/`, `core/`, `scripts/`, `tests/`, or `ui_common/` changes.
- No legacy `ui/` restoration.
- No PyQt production dependency reintroduction.
- No Arc 9.5 visual parity implementation.
- No prediction worker/progress/cancel implementation.
- No Trainer execution implementation.
- No ML algorithm, feature list, preprocessing, model artifact, mapping schema,
  calculator formula/config/fixture/golden/public-result changes.

## Verification

- `git diff --check`: passed.
- `git status --short`: checked during slice closeout.
- Stale old path search:
  `docs/ui_ux/06_PYSIDE6_VISUAL_AND_TABLE_PARITY_HARVEST.md` no longer appears
  in searched active docs outside archive.
- New path / asset / token search: confirmed references to the moved design
  harvest, `predict_ref_img.png`, `train_ref_img.png`, and
  `ui_common.visual_tokens`.
- Pytest: skipped, docs-only move/routing work.
- GUI smoke: skipped, no implementation or runtime UI change.
- Code map regenerate/check: skipped because workflow says the code map is for
  source-structure inventory and not default verification for docs/report-only
  changes.

## Slice Commits

- Slice 1: `e92ff63` docs(reports): audit pyside6 harvest location
- Slice 2: `2daf0a3` docs(reports): recover legacy ui harvest details
- Slice 3: `71e36a1` docs(ui): move pyside6 parity harvest to designs
- Slice 4: `0defb89` docs(ui): route pyside6 parity harvest through designs

## Active Report Count

- Before this closeout report: 16 active reports.
- After this closeout report: 17 active reports expected before any later
  lifecycle cleanup.

## Next Action

Arc 9.5 - Predict / Train Visual UI Parity from Design Assets.

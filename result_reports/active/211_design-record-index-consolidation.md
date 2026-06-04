# 211 — Design Record Index Consolidation

## Goal

Consolidate `docs/designs` management so individual design records are tracked through `docs/designs/README.md`, not as 18 separate active rows in `ACTIVE_DOCUMENTS.md`. This keeps `docs/designs` as a design gate evidence library rather than an active repeated-rule owner.

## Modified Files

- `docs/designs/README.md`
- `ACTIVE_DOCUMENTS.md`
- `AGENT_TASK_ROUTER.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/211_design-record-index-consolidation.md`

## Scope Confirmation

- Main was clean and up to date before edits.
- 209 identified design-record lifecycle/rule-source drift.
- 210 aligned the 18 actual design records with `ACTIVE_DOCUMENTS.md`.
- 211 consolidates that inventory into a dedicated index.

Not changed:

- Existing `docs/designs/*.md` design record bodies.
- `docs/archive/**`.
- `docs/architecture/**`.
- `docs/ui_ux/**`.
- Code files.
- Tests.

## Design README

Created `docs/designs/README.md` with:

- `docs/designs/` role as a design gate / decision record / evidence library.
- Explicit rule-owner principle: repeated rules live in UI/UX, architecture, standard/region docs, router, or WORK_PLAN.
- Lifecycle status definitions:
  - `template`
  - `active reference`
  - `absorbed by owner docs`
  - `historical reference`
  - `archive candidate`
- Compact index for all existing design records:
  - file
  - lifecycle status
  - one-line decision
  - current source of truth / owner doc
  - read trigger
- Update triggers for new design records, lifecycle/status changes, owner-doc mapping changes, and drift where a design record is treated as an active rule owner.
- Read rule: do not read all design records by default; use the index to pick the relevant record and then read only necessary ranges.

## ACTIVE_DOCUMENTS Cleanup

`ACTIVE_DOCUMENTS.md` Design Records now has one active owner row:

- `docs/designs/README.md` as design record index and lifecycle owner.

The 18 individual design records are no longer directly managed as active document rows there. They remain on disk and are indexed in `docs/designs/README.md`.

Added a maintenance rule that `docs/designs/README.md` should be updated when:

- a new `docs/designs/*.md` is added;
- lifecycle status changes;
- owner-doc mapping changes.

## Router Gate

Added a short Notes/document-refactor gate to `AGENT_TASK_ROUTER.md`:

- new design records, lifecycle/status changes, owner-doc mapping changes, or drift where design records are used as active rule owners require judging whether `docs/designs/README.md` needs an update;
- ordinary coding tasks should not read or update the design index by default.

## WORK_PLAN

Updated the current next action from generic Hong Kong CSPF batch smoke/polish to:

- `BatchCaseTable` keep/replace preflight;
- then correct Hong Kong CSPF batch table UX;
- then proceed to common detail/bin schema foundation.

## Verification

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing `ui_tk/sections/bin_detail_panel.py` soft LOC warning.
- `git status --short`: expected documentation/report changes only.

Not run:

- `pytest`: documentation/index cleanup only; no code/test changes.
- GUI smoke: no UI code changes.

## Next Action

Run `BatchCaseTable` keep/replace preflight. The decision should happen before implementation: adapt the existing batch table to meet the Tkinter table adapter contract, or replace it with a reusable table surface/controller pattern.

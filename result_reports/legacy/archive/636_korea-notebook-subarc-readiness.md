# KOREA Notebook Sub-Arc Readiness

## Goal

Start Calculator Sub-Arc - KOREA Notebook Entry with Slice 0 readiness work.

## Scope

- Promoted the root KOREA notebook sub-arc specification into the design record
  location required by the slice prompt.
- Updated the design records index so future KOREA calculator notebook work can
  find the active reference.
- Updated `docs/WORK_PLAN.md` with the active Slice 0 pointer and next Slice 1
  implementation pointer.

## Changed Files

- `docs/designs/2026-07-01-korea-notebook-entry-subarc-spec.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`

## Verification

- `git diff --check`: OK.
- File/path existence check for the design record and report: OK.
- `git status --short`: reviewed before commit.

## Known Risks

- The original root `korea_notebook_subarc_spec.md` remains tracked and was not
  moved or deleted because Slice 0 only allowed adding the design record and
  minimal work-plan updates.
- No source code was changed in this slice; implementation readiness still
  depends on Slice 1 reference-code audit before creating the KOREA tab
  skeleton.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: not run.

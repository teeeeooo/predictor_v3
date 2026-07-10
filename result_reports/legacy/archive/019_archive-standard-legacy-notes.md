# Archive Standard Legacy Notes

## Goal

Absorb reusable content from `docs/en14825_scop_notes.md` and `docs/skills/ahri_hspf2.md` into canonical standard docs, then move the legacy originals to archive.

## Scope

- Documentation-only migration for EN14825 and AHRI 210/240 standard notes.
- No calculator code, config, tests, public API, diagnostics schema, or golden expected changes.
- Preserve legacy originals under `docs/archive/standards_legacy/`.

## Changed Files

- `docs/en14825/en14825_dev_notes.md`: added preserved raw capacity-control step interpretation and air-to-air heating part-load condition temperatures.
- `docs/en14825/en14825_notes.md`: changed legacy note references from active support to historical archive.
- `docs/ahri210240/ahri210240_notes.md`: made canonical docs/code/tests the Primary basis and moved official comparison source references to archive.
- `docs/ahri210240/ahri210240_dev_notes.md`: updated Primary basis, golden source references, and prompt snippets away from `docs/skills/`.
- `docs/README.md`: updated the standard document map to point legacy helper docs at `docs/archive/standards_legacy/`.
- `docs/archive/standards_legacy/README.md`: added archive owner mapping and historical-source notice.
- `docs/archive/standards_legacy/en14825_scop_notes.md`: moved original legacy EN14825 SCOP note.
- `docs/archive/standards_legacy/ahri_hspf2.md`: moved original legacy AHRI HSPF2 note.
- `project_log.md`: recorded the notes absorption/archive decision.
- `result_reports/active/019_archive-standard-legacy-notes.md`: this compact result report.

## Verification

- `rg` active-path check: confirmed no `docs/en14825_scop_notes.md` or `docs/skills/ahri_hspf2.md` references remain outside `docs/archive/`.
- `rg` content check: confirmed canonical docs contain preserved raw step interpretation, air-to-air heating part-load table, AHRI official case references, H12/H22 source metadata, and defrost trace guidance.
- `git status --short`: confirmed scope is docs/report only.
- `git diff --check`: OK.
- Runtime tests were not run because this was documentation/archive migration only.

## Known Risks

- The archived legacy files intentionally preserve historical wording, including old self-references inside the original body.
- Future agents must treat `docs/archive/standards_legacy/` as historical evidence, not as active instruction.
- Lifecycle check found 8 active reports after this report; lifecycle maintenance is pending because doing it now would mix summary/archive maintenance into the current uncommitted docs migration scope.

## Commit / Push

- Source commit: not created in this turn.
- Report commit: not created in this turn.
- Push: not performed; no commit/push was explicitly requested.

# 464 Audit Calculator Legacy Entrypoint And Final Push

## Goal

Determine whether `app_calculator_tk.py` can be deleted, preserve the canonical
calculator launch boundary, and close the nine-task sequence with final
validation and one publication.

## Scope

- Audited code, README/project state, active guides, tests, scripts, packaging
  references, and the canonical application module.
- Retained or removed the legacy wrapper strictly from repository evidence.
- Updated the near-term work plan and recorded the final validation/publication.

## Non-goals

- No calculator behavior, profile, UI, sample, core, config, schema, fixture,
  golden, detail, or token migration changed.
- Historical design/archive references were not rewritten.

## Entrypoint Decision

`apps.calculator.app:main` is the canonical implementation entrypoint, and root
`app_calculator.py` is the documented canonical wrapper. Both README and
`project_brief.md` agree with this boundary.

`app_calculator_tk.py` is already a 10-line deprecated compatibility shim that
imports the exact canonical `main`; it owns no alternate shell or behavior. It
is not safe to classify as completely unused because:

- `docs/guides/lightweight_calculator_tk_manual_smoke.md` still exposes
  `python3 -B app_calculator_tk.py` as an external launch command;
- `docs/guides/lightweight_calculator_packaging_check.md` still uses it as a
  PyInstaller source entrypoint;
- `tests/test_apps_calculator_entrypoints.py` guards side-effect-free import and
  identity delegation to the canonical main.

Decision: retain the thin shim. Delete it only after those active guide commands
and the compatibility test are migrated or explicitly deprecated. Stale MVP
content inside the older guides is a separate documentation cleanup, not a
reason to silently break their entrypoint.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_entrypoints.py` — passed.
- `python3 -B tools/check_code_structure.py` — passed hard rules; existing EN
  section/adapter soft warnings only.
- The code-map check was stale after task 8 advanced local HEAD; regenerated
  once, then `--check` reported fresh before the task 9 commit.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — run after staging.
- Final local/remote SHA and clean status are recorded after the single push.

## Changed Files

- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/464_audit-calculator-legacy-entrypoint-final-push.md`

## Known Risks

- The two lightweight MVP guides contain broader historical UI assumptions;
  this audit treats their launch/packaging commands as compatibility consumers
  but does not modernize their full content.
- Removing the shim without first migrating those consumers would be a breaking
  external command change.

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

- `app_calculator_tk.py`, `app_calculator.py`, and `apps/calculator/app.py`;
  reason: compare shim and canonical owner.
- README/project brief entrypoint statements; reason: identify documented
  canonical launch path.
- active manual-smoke/packaging guide reference ranges; reason: determine whether
  external compatibility consumers remain.
- focused entrypoint tests and repository reference search; reason: verify import
  and delegation contracts.
- broad read: none; archive hits were classified as historical search evidence
  and not opened.

## Commit / Push

Task 9 is the ninth local commit. After final validation, all nine local commits
are pushed together exactly once; publication SHA evidence is filled by the
terminal handoff rather than embedding a self-referential pending hash here.

## Project Memory Delta

No memory-seed edit is required. The canonical entrypoint boundary is already in
project state; this report records why the deprecated wrapper remains.

## Next Suggested Action

Legacy UI token cleanup slices, following the formal inventory and keeping each
owner migration narrow.

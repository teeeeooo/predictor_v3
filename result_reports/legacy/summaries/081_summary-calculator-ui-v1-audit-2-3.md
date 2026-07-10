# 081 Summary: Calculator UI v1, Active Doc Inventory, Audit 2/3 Cycle

## Covered Reports

- `055_active-document-inventory-workflow.md`
- `056_audit-result-next-actions.md`
- `057_root-audit-result-lifecycle.md`
- `058_split-active-hspf-validation-helper.md`
- `059_app-calculator-ui-smoke-audit.md`
- `060_ahri-ui-profile-selector.md`
- `061_calculator-result-envelope-ml-adapter-design.md`
- `062_audit-2-next-actions-completion.md`
- `063_pyqt-ui-smoke-optional-guard.md`
- `064_connect-calculator-ui-result-action.md`
- `065_calculator-result-envelope-adapter-slice.md`
- `066_guard-calculator-schema-boundaries.md`
- `067_route-en14825-ui-through-profiles.md`
- `068_audit-3-next-actions-completion.md`

## Workstream Summary

### Active doc inventory & root audit lifecycle (055~057)

- Locked the active-document inventory workflow so future agents see the
  authoritative active set without scanning archive.
- Codified the "audit result next actions" and "root audit result"
  lifecycle so audits land in `reference_files/` and are then mirrored as
  individual active reports per task.

### Active HSPF validation helper split (058)

- Carved an HSPF validation helper out of the ISO active path without
  touching the calculator core, keeping the validation contract pure.

### Calculator UI v1 follow-up (059~060)

- Audited the `ui/calc_window.py` PyQt offscreen launch smoke surface and
  filled the gaps that the iso-separation work had left behind.
- Replaced filename-driven AHRI selector with explicit calculator profile
  selection (resolver-backed).

### Envelope / ML adapter design + first slice (061, 065, 066)

- Recorded the calculator result envelope / ML adapter boundary as the
  pre-implementation design doc
  (`docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`).
- Landed the first concrete slice of `CalculatorResultEnvelope` for
  `ahri_usa_seer2` in `core/calculator_result_adapter.py` without
  changing the calculator public API.
- Added a calculator schema boundary guard
  (`tests/test_calculator_schema_boundaries.py`) that pins import / region
  config / adapter-owned-term contracts.

### EN14825 SCOP UI wiring (064, 067)

- Connected the "계산 실행" button to a single UI result action shared by
  ISO / AHRI / EN tabs.
- Routed the EN14825 UI through calculator profile selection so SCOP
  selection follows the same dispatcher path as AHRI.

### Optional UI smoke guard + audit completions (063, 062, 068)

- Made the PyQt offscreen UI smoke gracefully skip when PyQt5 is
  unavailable so non-UI sandboxes do not regress.
- Closed audit 2 (062) and audit 3 (068) next-action cycles with
  per-cycle completion reports in `reference_files/`.

## Decisions Preserved

- Calculator result envelope, calculator input envelope, predicted-points
  envelope, and ranking-candidate envelope are adapter-owned, not part of
  calculator public APIs.
- Region config stays static standard data; runtime / ML / ranking
  vocabulary is blocked by the schema boundary guard.
- AHRI / EN selectors are driven by calculator profile resolver, not by
  filename scanning.
- PyQt5 missing environments skip the UI smoke tests by design.
- Per-audit completion reports live under `reference_files/` and are
  force-added through `.gitignore`.

## Verification Snapshot

- Latest full suite recorded in covered report `068` (audit 3
  completion): `301 passed, 23 xfailed`.
- Latest envelope / boundary check recorded in `066`: schema boundary
  guard passes on all 9 production region configs.

## Archive Candidates

Move covered active reports `055` through `068` to
`result_reports/archive/` without renaming.

## Project Log Sync Judgment

`project_log.md` update is NOT required at this summary level. The
calculator series reset decision (already recorded in the
`2026-05-17 — Calculator series reset direction` entry) and the
`2026-05-17 — Audit 4 next actions completion (069 ~ 073)` entry
together cover the architecturally meaningful decisions in this
workstream. Routine UI smoke audits, profile resolver wiring, and the
schema boundary guard are implementation follow-ups, not new
architecture rules.

# 591 - Code Map Freshness Fingerprint Fix

## Goal

Fix the code map freshness check so committing the generated code map no longer
makes `tools/code_checker/build_reference_map.py --check` stale immediately.

## Cause

Freshness previously compared the code map's stored `git_commit_short` with the
current HEAD. When a commit includes `docs/code_map/CODEBASE_REFERENCE_MAP.md`,
HEAD changes after the commit, so the committed map becomes stale even if the
code map inputs did not change. Regenerating repeatedly cannot solve that
commit-hash loop.

## Scope

- Added deterministic source fingerprint metadata for code map inputs.
- Changed freshness evaluation to compare source fingerprints, not commit hash.
- Kept `git_commit_short` and `git_dirty` as informational metadata.
- Marked pre-fingerprint metadata as `metadata_legacy` so regeneration is
  explicit.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` with metadata schema
  `1.1.0`.
- Updated focused code checker tests for deterministic fingerprinting,
  commit-hash mismatch handling, source-content stale detection, and legacy
  metadata handling.

## Modified Files

- `tools/code_checker/metadata.py`
- `tests/test_code_checker_reference_map.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/591_code-map-freshness-fingerprint-fix.md`

## Verification Results

- `python3 -B -m py_compile tools/code_checker/*.py`: OK.
- `python3 -B -m pytest tests -k "code_checker or reference_map or metadata"`:
  OK, 30 passed and 1312 deselected.
- `python3 -B tools/code_checker/build_reference_map.py`: OK, code map
  regenerated.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, status
  `FRESH` by source fingerprint.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings only.
- `git diff --check`: OK.
- `git status --short`: checked before commit.

## Excluded Scope

- No `apps/` production behavior changes.
- No `core/` ML, calculator, or mapping behavior changes.
- No Predict/Train UI changes.
- No Arc 11 Trainer execution work.
- No broad report lifecycle cleanup.

## Read Ledger

- `tools/code_checker/metadata.py`: full file, reason: freshness owner.
- `tools/code_checker/build_reference_map.py`: full file, reason: `--check`
  behavior and CLI boundary.
- `tools/code_checker/scanner.py`: relevant discovery function, reason:
  fingerprint input owner.
- `tests/test_code_checker_reference_map.py`: relevant metadata/freshness
  tests, reason: focused regression coverage.
- `tools/check_code_structure.py`: relevant code-map freshness warning adapter,
  reason: status compatibility.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: metadata/header check after
  regeneration.
- broad read: none.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `reuse_commonization: reused-existing-owner` because the fix stays inside the
  existing `tools/code_checker.metadata` owner instead of creating a parallel
  freshness path.

## Known Risks

- The regenerated map records `git_dirty: true` because this schema migration
  necessarily generated the map while tracked changes were present. That value
  remains informational only; freshness is based on `source_fingerprint`.

## Next Action

- Arc10 manual smoke.

## Commit / Push

- Commit after final validation.
- Push after commit.

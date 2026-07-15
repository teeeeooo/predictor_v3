```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase2-slice2d-exchange-export
  tags: train-admin, mapping, phase-2, slice-2d, exchange-export, csv, atomic-publish
  memory_review: updated
  memory_reason: Preserve the exchange/review ownership split, deterministic eight-file package contract, and exact-header import boundary for Slice 2E.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Implement the approved Slice 2D exchange export for Draft PR #15. The current
Data Mapping draft must be usable by external tools without exposing runtime JSON
or hidden backing payload, while the existing JSON/XLSX review snapshot remains
read-only and non-importable.

# Contract / Behavior Changed

- Added the Qt-free `mapping_bundle_v1` serializer and exchange export owner.
- One export operation creates seven canonical group CSVs and one freely named
  bundle CSV from the same service-owned draft.
- Group CSV and bundle section records share one visible-column serializer with
  deterministic UTF-8/LF bytes, canonical number/boolean text, PFC Pi blanking,
  and standard CSV quoting.
- Exchange export blocks error-level drafts, reserves case-insensitive canonical
  group filenames for the bundle, calculates all targets before writing, and
  stages/verifies the full package before publish with best-effort rollback.
- Existing `export_csv_v2` remains the Review Snapshot action. The compact Export
  menu now distinguishes Review Snapshot from Mapping Exchange Package; exchange
  export is disabled for invalid drafts.
- The initial Slice 2E exact-header decision is recorded: current visible
  projection headers are required exactly once, while header order remains free.

# Evidence And Verification

- `python3 -m pytest -q tests/core/mapping/test_exchange_export.py tests/test_apps_train_data_mapping_service.py tests/apps/train/ui/data_mapping/test_workflow.py tests/apps/train/ui/data_mapping/test_spreadsheet.py`
  passed 34 tests.
- Targeted Python compilation passed for the new exchange package and impacted
  service/controller/toolbar/panel modules.
- `python3 -B tools/check_code_structure.py --repo-root .` exited successfully;
  it reported only the existing warning-first hotspot/legacy warnings, including
  the known Data Mapping panel/service soft LOC warnings.
- `git diff --check` passed. Protected mapping fixtures and `data/mapping.json`
  are unchanged.

# Changed Files

- `core/mapping/exchange/` contract, serializer, target planner, and atomic
  staging/publish implementation
- Data Mapping service/controller exchange entry points and action metadata
- Data Mapping Export menu and exchange destination/overwrite confirmation path
- Focused exchange, service, workflow, and toolbar tests
- `docs/WORK_PLAN.md`, project memory seed, and this record/index entry

# Known Risks

- Publish is implemented as sequential same-directory replacements with staged
  backups and rollback; a filesystem failure that also prevents rollback can
  only preserve files to the extent the OS permits.
- Native visual evidence for this Batch is still pending and must remain bounded
  to rendering/screenshots; Slice 2B+2C physical interaction remains deferred.
- Slice 2E parser, preview/apply, stale-candidate safety, and Save/Reload
  round-trip are not included in this Slice.

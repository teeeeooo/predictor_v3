---
record:
  date: 2026-07-15
  topic: train-admin-phase2-slice2e-bundle-import
  tags: train-admin, mapping, phase-2, slice-2e, bundle-import, preview, round-trip
  memory_review: updated
  memory_reason: Preserve the exact-header import boundary, draft-only apply semantics, and bundle round-trip ownership for future audit.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
---

# Change Reason

Implement the approved Slice 2E sectioned `mapping_bundle_v1` import workflow
for Draft PR #15. The official bundle is the only normal import format; the
existing TSV clipboard path and JSON/XLSX review snapshots remain separate.

# Contract / Behavior Changed

- Added a Qt-free CSV parser, exact-header validator, typed candidate builder,
  canonical identity/diff owner, and service/controller preview/apply boundary.
- Every current visible group header, including optional dynamic columns, must
  occur exactly once. Header order is free; missing, unknown, duplicate, or
  structurally invalid content blocks the complete import and explains the
  group/column plus current Data Definition re-export path.
- Parser format and section identity come from CSV markers, never filename or
  extension. All seven sections are required, while a section may have zero
  data rows.
- Apply replaces the visible seven-group candidate in the service-owned draft,
  preserves matching hidden row payload and unowned sections, drops hidden
  payload for new rows, creates one grouped undo unit, and never writes the
  runtime mapping file or import source. Stale previews are rejected and
  semantic no-op imports do not create dirty state or undo history.
- Added a distinct `Import` toolbar action and compact production preview dialog
  showing source, format/version, affected groups, add/remove/change/unchanged
  counts, blockers/warnings, Save destination guidance, and explicit Cancel /
  Apply to Draft actions. Existing `export_csv_v2` remains Review Snapshot.
- Updated the DEV mock Train shell smoke assertion from the removed import
  placeholder to the actual Import and Export controls.

# Evidence And Verification

- Focused exchange/import/UI/smoke gate: 77 passed.
- Impacted mapping/Data Definition/Train regression: 189 passed.
- Full repository suite: 2051 passed, 2 xfailed after the smoke expectation
  correction.
- Targeted Python compilation passed for the new exchange parser/candidate,
  service/controller, preview dialog, toolbar, and panel modules.
- `python3 -B tools/check_code_structure.py --repo-root .` exited successfully;
  warning-first output contains only known existing hotspots, including the
  Data Mapping panel/service soft LOC warnings.
- `git diff --check` passed. Protected mapping fixtures and
  `data/mapping.json` are unchanged.
- Native visual evidence is still pending and remains bounded to rendering and
  screenshots; Slice 2B+2C physical interaction acceptance remains deferred.

# Changed Files

- `core/mapping/exchange/` import parser, typed candidate, identity, diff, and
  public facade
- Data Mapping service/controller/types and compact toolbar/panel preview UI
- focused import, workflow, service, UI-model, and mock-smoke tests
- `docs/WORK_PLAN.md`, project memory seed, and this record/index entry

# Known Risks

- Apply intentionally preserves only matching visible-row hidden payload; new
  rows receive no hidden payload and removed rows are not recoverable through
  the exchange file.
- The native screenshot path must use a synthetic temporary bundle and must not
  retry the known Computer Use Qt table accessibility crash.

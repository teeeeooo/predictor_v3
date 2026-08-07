record:
  date: 2026-08-07
  topic: data-mapping-drm-bootstrap-acquisition
  tags: windows, data-mapping, drm, legacy-bootstrap, xlwings, acquisition
  memory_review: no-change
  memory_reason: Current owner docs already preserve the Windows stabilization sequence; this record is point-in-time repair evidence and must not predeclare merge or native acceptance.

change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Data Mapping DRM-Sensitive Legacy Bootstrap Acquisition

## Change Reason

Native Windows acceptance found that a user-selected DRM-sensitive legacy Mapping
CSV can be opened by installed Excel automation but not by the ordinary Python
filesystem CSV read used by Data Mapping bootstrap.

## Contract / Behavior Changed

- Windows Train production composition selects a Data Mapping bootstrap-only
  `xlwings` acquisition adapter; non-Windows development retains the direct CSV
  adapter and ordinary Train/data CSV reads are unchanged.
- The dedicated Excel instance opens the selected CSV as UTF-8 raw Text lines
  with delimiter/quote parsing disabled. Those lines then use the existing Python
  CSV interpretation, strict legacy parser, and current Mapping Requirement
  validation, preserving per-row layout before semantic validation.
- Excel coercion, unexpected column splitting, or automation failure fails
  closed without direct-parser fallback. The source is never saved or rewritten,
  and only the workbook and Excel application created by this operation are
  closed.
- Successful bootstrap remains a validated Unsaved draft. Mapping Exchange and
  explicit Save retain their existing ownership; bootstrap does not publish
  `mapping.json`.

## Evidence And Verification

- Narrow acquisition + strict legacy/onboarding/cancel regressions: `37 passed`.
- Targeted Data Mapping adapter/application/UI/service/controller suite:
  `164 passed`.
- Real Windows + Excel + DRM smoke: NOT RUN / NOT AVAILABLE in the macOS Worker
  environment; native acceptance remains the post-merge confirmation owner.

## Changed Files

- `apps/train/adapters/mapping/legacy_bootstrap.py`
- `apps/train/adapters/mapping/windows_excel_legacy_bootstrap.py`
- `apps/train/adapters/mapping/__init__.py`
- `apps/train/composition/runtime.py`
- `tests/apps/train/adapters/mapping/test_windows_excel_legacy_bootstrap.py`
- `docs/development/dependencies.md`
- `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- `result_reports/REPORT_INDEX.md`
- this record

## Known Risks

Real protected-file behavior still depends on Windows, installed Excel, DRM
policy, and `xlwings` automation. Automated fakes prove composition, text-preserving
handoff, failure containment, and resource ownership but do not replace that
native smoke.

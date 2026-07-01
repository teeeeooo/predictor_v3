# 644 Summary - KOREA Calculator Sub-Arc Closeout

## Goal

Summarize and close the Calculator Sub-Arc - KOREA Notebook Entry reports from
design readiness through guide-table cleanup.

Covered reports:

- `636_korea-notebook-subarc-readiness.md`
- `637_korea-top-level-tab-skeleton.md`
- `638_korea-cspf-single-midpoint-guide.md`
- `639_korea-hspf-single-midpoint-guide.md`
- `640_korea-batch-dialogs.md`
- `641_korea-detail-view.md`
- `642_korea-subarc-closeout.md`
- `643_korea-guide-table-helper-cleanup.md`

## Major Decisions

- KOREA is a top-level Tk calculator notebook tab.
- The KOREA tab uses nested `CSPF` and `HSPF` metric pages.
- KS C 9306 CSPF/HSPF UI orchestration lives under
  `apps/calculator/application/korea/` and KOREA-specific Tk sections.
- Midpoint guide values are design helper values, not official KS C 9306
  results.
- Midpoint guide values stay out of official result dicts, batch outputs, and
  detail views.
- CSPF/HSPF batch dialogs reuse the existing batch matrix/dialog framework with
  KOREA-local input/result contracts.
- CSPF/HSPF detail views reuse the existing bin detail panel and show official
  `detail_rows` only.
- Repeated midpoint guide table UI presentation is isolated in
  `apps/calculator/ui/sections/korea_midpoint_guide_table.py`.

## Owner Changes

- `docs/designs/2026-07-01-korea-notebook-entry-subarc-spec.md`: active design
  reference for KOREA notebook entry slices.
- `apps/calculator/ui/tabs/korea_tab.py`: top-level KOREA tab and nested metric
  navigation.
- `apps/calculator/application/korea/`: KOREA CSPF/HSPF application usecases,
  result DTOs, and UI-neutral midpoint guide helpers.
- `apps/calculator/ui/sections/korea_cspf_section.py`: KOREA CSPF widget
  composition, event forwarding, result, batch, and detail wiring.
- `apps/calculator/ui/sections/korea_hspf_section.py`: KOREA HSPF widget
  composition, event forwarding, result, batch, and detail wiring.
- `apps/calculator/ui/batch_dialogs/profiles/korea_cspf.py`: KOREA CSPF batch
  matrix spec, row handler, adapter, and dialog wrapper.
- `apps/calculator/ui/batch_dialogs/profiles/korea_hspf.py`: KOREA HSPF batch
  matrix spec, row handler, adapter, and dialog wrapper.
- `apps/calculator/ui/sections/korea_midpoint_guide_table.py`: read-only
  KOREA midpoint guide table presenter.

## Runtime Behavior Changes

- `app_calculator.py` now exposes a `KOREA` top-level tab through
  `CalculatorTkApp`.
- KOREA CSPF single calculation supports declared capacity, 35 Full, 35 Half,
  and 29 Min inputs.
- KOREA HSPF single calculation supports rated cooling capacity, 7 Full,
  7 Half, 7 Min, 2 Defrost, and -7 Max inputs.
- KOREA CSPF/HSPF single screens display midpoint guide rows:
  current tc, recommended tc, and recommended Mid capacity.
- KOREA CSPF/HSPF batch tables calculate official metric summaries only.
- KOREA CSPF/HSPF detail panels display official bin detail rows only.

## Preserved Contracts

- No changes to `core/calculators/standards/ks_c9306.py`.
- No changes to `core/calculators/profiles.py`.
- No changes to `data/region_configs/korea.json`.
- No fixture/golden expected changes.
- No public result dict contract changes.
- No batch framework or detail framework rewrite.
- Train/Predict paths remained out of scope.

## Validation

- KOREA focused usecase, detail contract, batch profile, and tab construction
  tests were run across slices.
- Final closeout validation covered:
  - `python3 -B -m compileall -q apps/calculator core/calculators tests`: OK.
  - KOREA focused pytest selection: OK with headless Tk skips.
  - profile/dispatcher focused tests: OK.
  - `python3 -B tools/check_code_structure.py`: OK with existing warnings
    outside the KOREA source changes.
  - `git diff --check`: OK.
- Follow-up guide-table helper cleanup validation covered:
  - `python3 -B -m compileall -q apps/calculator tests`: OK.
  - KOREA focused pytest selection: OK with headless Tk skips.
  - `python3 -B tools/check_code_structure.py`: OK with existing warnings and
    a code-map freshness reminder, later resolved by a reference-map refresh.

## Remaining Risks

- Tk visual/manual smoke was not run in the headless environment. Manual smoke
  remains useful for visible tab switching, dialog open/preserve behavior,
  detail toggle/refit, and scroll/viewport behavior.
- KOREA CSPF/HSPF section files remain above the 250 LOC soft planning
  threshold, although duplicated guide table presentation was extracted.
- Memory seed compaction remains a dedicated maintenance task because the seed
  already exceeds the dedicated maintenance threshold.

## Lifecycle

- Active reports `636-643` are covered by this summary.
- Covered reports are archived under `result_reports/archive/`.
- `result_reports/memory/project_memory_seed.md` is updated with the summary
  registration and one compact durable KOREA decision entry.

## Next Action

Arc 13.5 Slice 0 - Feature Catalog Editor Design Gate.

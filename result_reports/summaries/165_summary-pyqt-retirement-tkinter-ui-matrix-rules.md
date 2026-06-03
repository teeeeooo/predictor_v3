# Summary: PyQt Retirement Hold / Tkinter UI Matrix Rules

## Summary Scope

This lifecycle summary consolidates active reports 154-164, including report
159, into one searchable record of the PyQt calculator retirement boundary,
Tkinter calculator final-UX implementation arc, and the resulting project-wide
visual/input/result UI rules. The workstream spans decisions, narrow code
foundations and vertical slices already completed in the covered reports; this
maintenance task changes documentation, lifecycle placement, and memory/log
indexes only.

At task start the working tree was clean on
`work/ui-ux-ssot-adoption`. Existing summaries ended at report 153, so the
requested summary number 165 does not conflict with an existing summary.

## Covered Reports

| Report | Topic | Lifecycle disposition |
| --- | --- | --- |
| `154_pyqt-calculator-retirement-audit.md` | PyQt calculator-only retirement audit | archive after summary |
| `155_pyqt-calculator-direct-test-retirement.md` | Direct calculator-only test retirement | archive after summary |
| `156_shared-pyqt-utility-retention-decision.md` | Shared PyQt utility hold decision | archive after summary |
| `157_tkinter-final-ux-contract-alignment-audit.md` | Tkinter final UX contract and retirement gate | archive after summary |
| `158_project-wide-visual-design-architecture-adoption.md` | Project-wide visual architecture SSOT | archive after summary |
| `159_track-visual-inspiration-source-reference.md` | Inspiration source reference tracking | archive after summary |
| `160_toolkit-visual-token-foundation.md` | Toolkit-neutral visual token foundation | archive after summary |
| `161_tkinter-table-grid-input-foundation.md` | Tkinter table/grid model and adapter foundation | archive after summary |
| `162_tkinter-iso-hk-table-autocalc-vertical-slice.md` | Hong Kong table + auto-calc vertical slice | archive after summary |
| `163_tkinter-iso-hk-input-output-ui-correction.md` | Hong Kong matrix/summary UI correction | archive after summary |
| `164_project-wide-input-matrix-result-surface-rules.md` | Project-wide matrix/result surface rules | archive after summary |

Report 159 was not listed as an implementation milestone in the initial
background, but it is active and belongs to this arc because it records the
reference-source status supporting the visual architecture adoption.

## Key Decisions

1. PyQt calculator-only source retirement remains held.
2. Direct PyQt calculator tests were retired, while shared PyQt utilities and
   guarded widget support remain retained/hold assets for a later decision.
3. Tkinter calculator final UX is table/grid input plus auto-calc, not Entry
   rows plus calculate buttons.
4. Tkinter ISO Hong Kong CSPF/HSPF now use matrix-style input and summary
   result surfaces while retaining the existing calculation route and default
   smoke outcomes.
5. Project-wide visual architecture and toolkit-neutral visual token
   foundation exist; existing semantic engineering colors are not discarded.
6. Project-wide input matrix/result surface rules now govern repeated
   structured input and primary result UI shaping.
7. Graph/detail surfaces are deferred to a lightweight design phase; large
   graph dependencies remain deferred before Windows packaging evidence.
8. Following user review of the 163 visible output, the next implementation is
   matrix/result visual surface refinement; manual smoke follows refinement.

## Completed Work

- Reports 154-156 separated calculator-only PyQt retirement candidates from
  retained Predict/Train and shared PyQt support, retired direct tests, and
  held shared utility removal.
- Report 157 established the Tkinter final UX and retirement dependency.
- Reports 158-160 established project-wide visual architecture, tracked the
  inspiration reference as non-SSOT source material, and introduced the
  toolkit-neutral semantic visual token foundation.
- Reports 161-163 delivered the Tkinter table/grid foundation, auto-calc
  integration, and first Hong Kong matrix-input/summary-result UI slice.
- Report 164 promoted the observed matrix/result shaping need into a
  project-wide UI/UX SSOT rule.

## Deferred / Held Work

- PyQt calculator source retirement remains held until later Tkinter
  UX/packaging judgment.
- Tkinter matrix/result visible surface refinement remains required before the
  next macOS manual UX smoke.
- Lightweight graph/detail design remains optional follow-up work and is not a
  replacement for summary result surfaces.
- Windows PyInstaller size measurement remains pending a Windows host.
- Toolkit visual token foundation exists but full widget/style adoption is not
  part of this lifecycle step.

## UI/UX SSOT Changes

- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` owns project-wide neutral-first
  visual architecture with semantic engineering-color preservation.
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` owns repeated-input
  matrix shaping and summary-result surface rules across Calculator,
  Predict/Train, and future ML/inverse-search UI.
- The Figma-inspired file under `docs/ui_ux/_source/` is reference source
  material, not active SSOT.
- The Tkinter final UX contract is registered as an active design record in
  `ACTIVE_DOCUMENTS.md` during this lifecycle sync.

## Tkinter Calculator Status

The Hong Kong CSPF/HSPF path has table/grid input, auto-calc, and summary
result output with default CSPF `4.939` and HSPF `3.643` retained in its
verified slice. The user subsequently confirmed that the visible 163 surface
still differs from the intended UI; therefore its next step is visual surface
refinement implementation, not a final manual acceptance smoke.

## PyQt Calculator Retirement Status

`app_calculator.py` and its calculator-only PyQt modules remain retirement
candidates, but no source retirement is performed here. The retirement gate
remains Tkinter UX/packaging judgment; the implementation sequence now includes
visible matrix/result refinement before manual smoke and later packaging
evidence.

## Shared PyQt Utility Status

`ui/spreadsheet_table.py`, `ui/theme.py`, their retained tests, and PyQt
environment support remain quarantine/hold assets rather than calculator-only
retirement collateral. PyQt Predict/Train remains outside calculator-only
retirement scope.

## Graph / Detail Surface Status

Existing PyQt graph/detail behavior remains reference UX. Tkinter graph/detail
work, if needed, will be designed as a separate lightweight surface after the
summary result direction is stable. `matplotlib` or similarly large
dependencies are not introduced before Windows packaging size judgment.

## Active Docs Sync

- Already registered before lifecycle maintenance:
  `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`,
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`,
  `docs/guides/lightweight_calculator_tk_manual_smoke.md`, and
  `docs/guides/pyqt_test_support_matrix.md`.
- Added minimally during maintenance:
  `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`.
- `docs/WORK_PLAN.md` records lifecycle completion and updates the next action
  order so implementation refinement precedes manual smoke.

## Project Log Sync

**Judgment:** `update needed`.

**Reason:** Reports 154-164 form a milestone arc: the PyQt retirement hold,
Tkinter matrix/summary direction, and project-wide surface SSOT are durable
decisions not covered by the existing recent log entries.

**Action:** Add one concise `2026-05-24` milestone entry to `project_log.md`.

## Project Memory Seed Sync Judgment

**Judgment:** `update needed`.

**Reason:** The seed already captures earlier Tkinter/PyQt feasibility and
workflow policy, but not the project-wide visual/matrix/result SSOT decision or
the Hong Kong matrix UI plus PyQt retirement gate state consolidated here.

**Action:** Add exactly two summary-level decision entries, sourced to this
summary; do not copy individual report deltas or modify importance/aging.

## Archive Candidates

All covered active reports 154-164, including 159, are archive candidates.
They are moved with filenames unchanged after this summary is written.

## Active After

After the covered files are moved, `result_reports/active/` is expected to
contain no remaining report files. Verification below records the actual
post-move state.

## Next Actions

1. Tkinter matrix/result visual surface refinement implementation.
2. macOS Tkinter manual UX smoke, refinement 이후.
3. Lightweight graph/detail surface design, 필요 시.
4. Windows PyInstaller size measurement, Windows host available 시.
5. Tkinter standard/region expansion, 필요 시.
6. PyQt calculator source retirement 재검토, Tkinter UX/packaging 판단 이후.

## Verification

- `python3 -B tools/check_code_structure.py`: PASS
  (`code structure guard: OK (no findings)`).
- `python3 -B -m pytest -q -rxXs`: PASS
  (`629 passed, 32 skipped, 19 xfailed in 2.17s`), unchanged from the
  document-only/lifecycle baseline and without native abort.
- `result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`
  exists; covered reports `154`-`164` are present under
  `result_reports/archive/` with unchanged filenames.
- `find result_reports/active -maxdepth 1 -type f | sort` produced no report
  paths after archive movement.

## Commit / Push

- This summary, its archive moves, and the minimal active-doc/work-plan/log/
  memory-seed sync are committed together as one lifecycle maintenance unit.
- Commit hash and push status are reported after the finalized report is
  committed.

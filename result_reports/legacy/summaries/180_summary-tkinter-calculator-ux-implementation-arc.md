# Summary: Tkinter Calculator UX Implementation Arc

## Summary Scope

This lifecycle summary consolidates active reports 166-179e into one record
of the Tkinter calculator UX implementation, refinement, and contract
amendment arc that followed the 165 summary (covered reports 154-164). The
workstream spans visible surface refinement, responsive architecture,
Excel-like interaction foundation, window geometry/scroll fixes, smoke-loop
operating rules, and the metric sub-tab design amendment.

At task start the working tree was clean on `work/ui-ux-ssot-adoption`.
Existing summaries ended at report 165, so summary number 180 does not
conflict.

## Covered Reports

| Report | Topic | Lifecycle disposition |
| --- | --- | --- |
| `166_tkinter-matrix-result-visual-surface-refinement.md` | Matrix/result visible surface refinement | archive after summary |
| `167_pyqt-calculator-reference-feature-migration-contract.md` | PyQt reference feature migration contract | archive after summary |
| `168_tkinter-iso-hk-layout-correction.md` | ISO HK layout correction | archive after summary |
| `169_tkinter-table-card-width-alignment-refinement.md` | Table/card width alignment | archive after summary |
| `170_tkinter-responsive-table-architecture-alignment.md` | Responsive table architecture | archive after summary |
| `171_ui-ux-portable-visual-value-ownership-cleanup.md` | Portable visual value ownership | archive after summary |
| `172_tkinter-excel-like-table-behavior-controller.md` | Excel-like table controller | archive after summary |
| `173_tkinter-excel-like-ux-smoke-fix.md` | Excel-like UX smoke fix | archive after summary |
| `174_tkinter-excel-like-selection-clear-fix.md` | Selection clear fix | archive after summary |
| `175_excel-like-table-state-machine-contract.md` | Selection/edit state machine contract | archive after summary |
| `176_tkinter-excel-like-edit-mode-implementation.md` | Edit mode implementation | archive after summary |
| `177_tkinter-edit-cross-table-commit-and-window-centering.md` | Cross-table commit and window centering | archive after summary |
| `178_tkinter-initial-window-size-and-scroll.md` | Initial window size and scroll | archive after summary |
| `179a_workflow-tokenization-guard-update.md` | Workflow/tokenization guard update | archive after summary |
| `179e_tkinter-calculator-metric-subtab-design-amendment.md` | Metric sub-tab design amendment | archive after summary |

Reports 179-b/179-c/179-d were source-only smoke-loop diagnostics without
active reports and are not backfilled. They are acknowledged as smoke-loop
iterations between formal reports.

## Key Decisions

1. Tkinter ISO Hong Kong CSPF/HSPF matrix input, auto-calc, and summary
   result surfaces were refined through visible widget layers while keeping
   core/profile/dispatcher routes and smoke values unchanged.
2. `MetricInputTable` exposes address lookup and notify-once batch mutation
   APIs; interaction logic is owned by a separate `ExcelLikeTableController`
   that attaches to the table metadata surface.
3. Excel-like selection/edit state machine (selection mode, edit mode,
   type-to-replace, same-cell second click/double click/F2, Esc/focus loss,
   cross-table commit) was contracted in `03_SPREADSHEET_TABLE_UX_CONTRACT.md`
   and implemented in the Tkinter adapter.
4. UI smoke-loop mode and diff/read budget rules were added to
   `AGENT_TASK_ROUTER.md` to reduce token-heavy micro-fix churn.
5. Window geometry policy values (screen ratios, margins, caps, min/max) must
   live in a toolkit-local layout owner (`ui_tk/layout_constants.py`), not in
   app shell modules.
6. The Tkinter calculator final UX contract was amended: top-level standard
   tabs and region selectors remain; metric sub-tabs or equivalent segmented
   metric navigation inside a standard tab are permitted when content density
   is high. CSPF/HSPF same-view is the default but metric separation is now
   recommended for ISO Hong Kong.
7. EN 14825 (SEER/SCOP) and AHRI 210/240 (SEER2/HSPF2) are linked to the same
   metric-navigation principle.

## Completed Work

- Visible matrix/result surface refinement for ISO Hong Kong (166).
- Layout correction separating rated and trial-input surfaces per metric
  (168).
- Table/card width alignment and responsive stretch architecture (169-170).
- Portable visual value ownership cleanup; constants moved out of component
  locals (171).
- Excel-like table behavior controller with rectangular selection, TSV
  copy/paste, Delete/Backspace clear, grouped undo, Tab/Enter navigation
  (172).
- macOS manual smoke fixes for selection clear, edit-mode behavior, and
  cross-table commit (173-174, 176-177).
- Selection/edit state machine contract aligned across Tkinter and PyQt
  adapters (175).
- Initial window geometry capped to screen bounds; canvas-based vertical
  scroll for tall content (178).
- Workflow/tokenization guard and layout-constant ownership rules (179a).
- Final UX contract amendment permitting metric sub-tabs (179e).

## Smoke-loop / Workflow Decisions

- UI manual-smoke micro-fixes may use smoke-loop mode: source/test only, no
  WORK_PLAN/report/project_log/memory seed updates, focused tests only.
- Stable checkpoint mode may briefly update docs once the user confirms the
  loop is stable.
- Diff/read budget: name-only → stat → `rg`/`sed` small ranges → narrow hunk
  reads; pytest detail is failure-centered.

## Deferred / Held Work

- ISO Hong Kong CSPF/HSPF metric sub-tab implementation is the next
  recommended action, not yet started.
- Window geometry/scroll may need further refinement after sub-tab
  separation.
- Graph/detail surfaces remain a lightweight Canvas-oriented later phase.
- `matplotlib` or similarly large dependencies must not be introduced before
  Windows packaging size evidence.
- EN 14825, AHRI 210/240, KS C 9306 tab expansion remains future work.

## Tkinter Calculator Status

- The Tkinter calculator (`app_calculator_tk.py` thin entrypoint +
  `ui_tk/calculator_app.py` shell + `ui_tk/tabs/iso16358_tab.py` +
  sections + controller) is the active UX implementation path.
- Hong Kong CSPF 4.939 / HSPF 3.643 smoke values are retained.
- Matrix input, auto-calc, and summary result surfaces are implemented.
- Excel-like interaction (selection, edit, clipboard, undo, navigation) is
  implemented.
- The final UX contract amendment allows metric sub-tabs for high-density
  cases; same-view vertical stack is the default but metric separation is
  recommended for ISO Hong Kong.

## PyQt Calculator Retirement Status

- `app_calculator.py` and its calculator-only PyQt modules remain retirement
  candidates, but no source retirement is performed here.
- The retirement gate is: Tkinter vertical slice verified + Windows packaging
  size meets continue criteria + explicit usability decision.
- Shared PyQt utilities remain retained/hold.
- Reports 154-156 identified the retirement candidates and ordered the
  slices. Task 162 satisfied the Hong Kong vertical-slice prerequisite but
  did not authorize S3 (source retirement).

## Graph / Detail Surface Status

- Existing PyQt graph/detail behavior remains reference UX.
- Tkinter graph/detail design remains optional follow-up work.
- Summary result direction is stable.

## Project Log Sync Judgment

**Judgment:** `update needed`.

**Reason:** The last `project_log.md` entry is dated 2026-05-24 (Tkinter
matrix UI direction + surface rules). The 166-179e arc adds durable
decisions: Excel-like state machine, smoke-loop operating rules, metric
sub-tab amendment.

**Action:** Append one concise milestone entry summarizing the arc and its
key decisions/lessons.

## Project Memory Seed Sync Judgment

**Judgment:** `update needed`.

**Reason:** The seed captures the 165 summary (154-164) but does not yet
contain durable entries for the Excel-like state machine/selection-edit
semantics or the metric sub-tab amendment.

**Action:** Add exactly two summary-level decision entries sourced to this
summary; do not copy individual report deltas or modify importance/aging.

## Archive Candidates

All covered active reports 166-179e, including 167, are archive candidates.
They are moved with filenames unchanged after this summary is written.

## Active After

After the covered files are moved, `result_reports/active/` is expected to
contain no remaining report files. Verification below records the actual
post-move state.

## Next Actions

1. **ISO Hong Kong CSPF/HSPF metric sub-tab implementation** — introduce
   metric sub-tabs inside `ui_tk/tabs/iso16358_tab.py` and run manual smoke.
2. Continue geometry/scroll refinement if width/height issues persist after
   sub-tab separation.
3. Tkinter matrix/result spacing or semantic styling refinement only if
   manual smoke exposes a need.
4. Lightweight graph/detail surface design, if justified later.
5. PyQt calculator source retirement 재검토, Tkinter UX/packaging 판단 이후.

## Verification

- `python3 -B tools/check_code_structure.py`: passed.
- `git diff --check`: clean.
- Only docs, report, and archive lifecycle files modified; no Python
  source/test changes.
- `result_reports/active/` post-move state: see Active After.

## Commit / Push

- Lifecycle maintenance commit with summary, log, seed, and archive moves.
- Separate commits for docs/log/seed vs summary vs archive moves.
- Push to `work/ui-ux-ssot-adoption`.

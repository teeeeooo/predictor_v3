# 445 Summary - AHRI Calculator UI/Batch Lifecycle Closeout

## Goal

Close the completed AHRI 210/240 calculator UI/batch arc and preserve its
durable workflow, token, sizing, and adapter-boundary decisions in one anchor.

## Scope

- Covered reports 417-444.
- Closed the EN14825-to-AHRI transition, AHRI design/main/batch implementation,
  sizing corrections, UI literal gate foundation, and publication workflow.
- User-confirmed final AHRI HSPF2 batch visual readability completes the manual
  smoke evidence.

## Closed Product Results

- SEER2 and HSPF2 are separate AHRI metric surfaces. SEER2 supports HP/AC Type;
  HSPF2 owns Region IV options, heating points, and its A2 cooling anchor.
- Both metrics have automatic two-physical-row BatchMatrix workflows with
  snapshot/reopen lifecycle and duplicate-dialog prevention.
- HSPF2 A2 accepts capacity only. The adapter supplies the positive tuple-shape
  placeholder required by the unchanged core validator.
- H42/H12/H22 optional input state separates draft common values, last-valid
  active options, and a hidden superset case store. Disabled point keys are
  omitted from core input and restored when re-enabled.
- Source normalization remains in the HSPF2 adapter/main UI. HSPF2 batch output
  was deliberately simplified to the primary HSPF2 result only.
- SEER2 and HSPF2 seasonal totals use existing core returns and UI-boundary
  display scaling; no core equation/public-result contract changed.

## Closed Sizing and Table Decisions

- AHRI visible-content diagnosis rejected profile wrapper removal and corrected
  common nested-notebook chrome-height arithmetic instead.
- BatchMatrix Case/Row Type widths and result/point widths use common semantic
  tokens. Leading columns do not absorb shared expansion weight.
- The vertical batch viewport never compresses content below its natural
  requested width. Batch dialogs propagate natural width/height into the
  existing screen-capped, parent-centered initial geometry policy.
- Fixed geometry, profile min-size inflation, and narrower data tokens are not
  accepted substitutes for natural content fitting.

## Closed Workflow Decisions

- The staged agent-change checker is connected to opt-in pre-commit and
  commit-msg hooks; publication completion requires local/remote SHA equality.
- Focused verification runs once unless failure or relevant source/test/report
  changes justify a rerun.
- Phase 1 UI magic-literal enforcement blocks new staged production UI width,
  min-size, fixed geometry, and color literals outside semantic token owners;
  legacy inventory/migration remains a separate formalization slice.

## Mock Data Judgment

`apps/calculator/ui/ahri/hspf2_mock_data.py` remains a clearly named, isolated
DEV sample owner. It does not affect core/config/fixture/golden contracts and is
not a lifecycle blocker. Removing initial sample population changes empty-state
product behavior and therefore requires a separately approved product decision;
it is not folded into this docs-only closeout.

## Archived Reports

- Workflow/transition: 417-424.
- AHRI design and SEER2: 425-429, 432.
- HSPF2 main/batch: 430-431, 433, 440-441, 444.
- Visible sizing diagnosis/corrections: 434-436, 439, 442-443.
- UI literal gate foundation/hardening: 437-438.

The exact archived filenames are recorded in lifecycle report 446. No covered
report retains a current blocker or next-decision role.

## Documentation and Memory Sync

- `project_brief.md`: AHRI Arc 2 marked complete; Arc 3 preparation unblocked.
- `docs/WORK_PLAN.md`: next action reduced to UI magic literal legacy inventory
  formalization.
- `project_log.md`: milestone decision recorded.
- `result_reports/memory/project_memory_seed.md`: this summary registered and
  two durable decisions added.

## Verification

- User manual AHRI HSPF2 batch visual recheck: complete.
- Lifecycle path uniqueness, summary coverage, and remaining-active reasons:
  checked during report 446.
- Docs-only validation uses `git diff --check` and the staged change gate.

## Known Risks

- Natural batch width beyond the screen cap still needs a separately designed
  horizontal-navigation fallback if a real profile requires it.
- The memory seed remains above its audit-candidate threshold but below its
  mandatory dedicated-maintenance threshold.

## Next Action

UI magic literal legacy inventory formalization.

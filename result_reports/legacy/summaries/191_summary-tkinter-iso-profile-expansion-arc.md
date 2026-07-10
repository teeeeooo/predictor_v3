# 191 Summary - Tkinter ISO Profile Expansion Arc

## Summary Scope

This summary covers the active reports created after `180_summary-tkinter-calculator-ux-implementation-arc.md`, from portable Tkinter geometry rules through ISO/ISEER 2-point adoption, result display refinement, profile-switch polish, and SASO T3 design.

Grouping: **Tkinter ISO profile expansion arc**.

## Covered Reports

- `184_portable-window-geometry-rule-update.md`
- `185_tkinter-shell-geometry-scroll-cleanup.md`
- `186_pyqt-reference-parity-audit.md`
- `187_iso-iseer-2point-tkinter-design-slice.md`
- `187b_iso-iseer-2point-tkinter-implementation.md`
- `187c_iso-profile-selector-ia-correction.md`
- `188a_design-first-gate-update.md`
- `189a_iso-iseer-2point-result-visual-refinement-design.md`
- `189b_iso-iseer-2point-result-visual-refinement.md`
- `189c_profile-switch-window-fit-scroll-hotfix.md`
- `189d_profile-switch-grow-fit-scroll-reset.md`
- `189e_profile-switch-default-exact-fit-hotfix.md`
- `190a_saso-t3-design-and-docs-cleanup.md`
- `190a2_saso-t3-result-comparison-design-amendment.md`

## Main Decisions

- Tkinter calculator window geometry and scroll behavior are owned by toolkit-local helpers and `ScrollableFrame`, not by ad hoc shell constants or root/toplevel `<Configure>` loops.
- PyQt calculator code remains a reference source for feature parity auditing; Tkinter work proceeds by focused slices rather than direct wholesale porting.
- The ISO tab uses an `ISO 프로파일` selector. The default profile is `ISO / ISEER 2-point`; `Hong Kong` remains available with CSPF/HSPF metric sub-tabs.
- High-impact UI changes now pass through Design First Gate: design slice first, implementation slice second. Hotfix and micro cleanup remain scoped exceptions.
- ISO/ISEER 2-point primary results use a section-local read-only comparison table rather than stacked `ResultPanel` summaries.
- Profile switch geometry now exact-fits to the currently rendered profile preferred size, then applies one measured-overflow height correction and resets scroll to top.
- SASO T3 should be added as a dedicated Tkinter section using the existing `saso_t3_cspf` profile/config path. Its result surface should compare required-only 3-point and optional-min 4-point scenarios.

## Implementation Outcomes

- Tkinter ISO/ISEER 2-point profile was added and made the default ISO tab profile.
- ISO/ISEER 2-point calculates and displays `ISO 16358-1` and `India ISEER` rows with `EER Full`, `EER Half`, `CSPF/ISEER`, `CSTL [kWh]`, and `CSEC [kWh]` columns.
- Invalid 2-point input clears stale success values and shows safe status without raw dict, traceback, or `None` leakage.
- Hong Kong CSPF/HSPF result display stayed on the existing `ResultPanel` path.
- No-overflow wheel events no longer scroll into blank space; overflowing content still scrolls.
- Profile switching between ISO/ISEER 2-point and Hong Kong exact-fits the current profile and avoids persistent blank trailing space.

## Manual Smoke Outcomes

- ISO/ISEER 2-point default load, comparison table rendering, input recalculation, invalid input handling, and Hong Kong profile switching were manually checked across the 187/189 slices.
- The 189-e exact-fit policy was manually confirmed by the user as matching intent. Geometry polish is closed for this arc unless a new concrete issue appears.

## Design First Gate / Token Budget Updates

- Design First Gate was documented for larger UI/architecture-sensitive work.
- Diff/read budget guidance was tightened so already-read policy/design sections are reused within the same session and long compliance reprints are avoided.

## Result / UI / Geometry Decisions

- `ResultPanel` remains unchanged. Specialized comparison surfaces stay section-local until a stronger reuse case exists.
- ISO/ISEER 2-point and future SASO comparison tables are read-only result surfaces, not editable input tables.
- Profile/tab geometry should use current rendered preferred size, not hardcoded per-profile geometry tables or cached static sizes.
- If future dynamic surfaces such as graph/detail change rendered size after calculation, their preferred-size owner needs a separate design slice.

## SASO T3 Design Decision

- Add `SASO T3` as an ISO profile selector option with a dedicated SASO section.
- Required input points: `46 Full`, `35 Full`, `35 Half`.
- Optional input point: `35 Min`.
- Toggle off shows required-only 3-point result.
- Toggle on with valid `35 Min` shows both `Required only (3-point)` and `With 35 Min (4-point)` rows.
- Toggle on with invalid/incomplete `35 Min` may keep the 3-point result visible while the 4-point row shows safe status/error.
- SASO implementation is not complete in this summary.

## Remaining Known Risks

- SASO T3 implementation still needs focused source/test work.
- SASO result comparison depends on calculator instance config override behavior for required-only vs optional-min selection.
- Future hidden tab, graph/detail, or other dynamic result surfaces may require explicit preferred-size ownership.
- SASO multi/batch/detail/graph and EN/AHRI remain excluded.
- `docs/WORK_PLAN.md` has become large and should be compacted in a separate docs-only reset slice before more long-running implementation work.

## Next Action

Recommended next docs-only action: **WORK_PLAN compaction / current execution reset**.

After that reset, proceed with **190-b SASO T3 implementation slice**:

- Add a dedicated `IsoSasoT3Section`.
- Keep source changes focused on SASO T3 input, optional 35 Min toggle, and section-local 3-point vs 4-point result comparison.
- Add focused tests for toggle off, toggle on valid, toggle on invalid, stale value clearing, and ISO/ISEER/Hong Kong non-regression.

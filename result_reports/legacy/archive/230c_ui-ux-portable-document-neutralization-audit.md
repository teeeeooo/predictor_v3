# 230C — UI/UX Portable Document Neutralization Audit

## Goal

Audit `docs/ui_ux/` as a portable UI/UX documentation set. This task does not
rewrite UI/UX documents. It classifies documents, identifies project/toolkit
specific wording that leaks into principle sections, and defines a small 230D
neutralization slice.

## Checked Documents

- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/ui_ux/06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `ACTIVE_DOCUMENTS.md` UI/UX rows
- `docs/WORK_PLAN.md`
- recent `project_log.md` entries
- `result_reports/active/230b_clean-architecture-boundary-wording-neutralization.md`

## Document Classification

| Document | Classification | Judgment |
| --- | --- | --- |
| `00_UI_UX_SYSTEM.md` | portable principle document | Mostly portable. Some related-doc labels mention current project bindings, but the root role is clear. |
| `01_TOOLKIT_SELECTION_POLICY.md` | portable principle document with toolkit-choice policy | Toolkit names are expected because the document decides toolkit choice. No neutralization priority. |
| `02_DESIGN_TOKENS_AND_LAYOUT.md` | portable principle document | Mostly portable. Concrete owner examples are acceptable; low priority. |
| `03_SPREADSHEET_TABLE_UX_CONTRACT.md` | portable principle document | Strong portable contract. One related-doc line names current project matrix/result rules; low priority. |
| `04_VISUAL_DESIGN_ARCHITECTURE.md` | intended portable principle, currently project-binding heavy | High neutralization need. Purpose/scope/adoption sections read current-project-specific. |
| `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` | intended portable principle, currently project-binding heavy | High neutralization need. Purpose/scope/examples/adoption mix current project and toolkit names into principle text. |
| `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md` | project-binding/adoption document | Already describes how to adopt common docs into another project. Keep. |
| `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` | portable principle document with observed examples | Medium neutralization need. Scope lists concrete implementations; WPF guide is implementation-specific. |
| `adapters/PYQT_TABLE_IMPLEMENTATION.md` | toolkit adapter document | Specific toolkit names are normal. Exclude from neutralization. |
| `adapters/TKINTER_TABLE_ADAPTER.md` | toolkit adapter document | Specific toolkit/project binding examples are normal, though some current-project notes may be reviewed later if they override common contracts. |
| `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` | historical/source/reference document | Active contract does not live here. Exclude. |

## Specificity Audit

### `04_VISUAL_DESIGN_ARCHITECTURE.md`

Neutralization need: High.

Findings:

- Purpose says it is the `predictor_v3` visual SSOT.
- Scope names Predict/Train PyQt surfaces and Tkinter calculator direction.
- Toolkit adaptation and application notes mix principle with PyQt/Tkinter
  adoption details.
- Adoption order is a current-project roadmap, not a portable visual principle.

Recommendation:

- Keep the visual principles, semantic roles, neutral-first chrome, table-first
  interaction, typography, spacing, focus, and result/status surfaces.
- Move or relabel concrete project/toolkit references into an
  `Adoption / Evidence Notes` section.
- Make purpose portable: "common visual design architecture for engineering
  desktop/data tools" rather than current-project SSOT.
- Keep exact project rollout steps only as project adoption notes or remove
  from the portable principle body.

Include in 230D: Yes.

### `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`

Neutralization need: High.

Findings:

- Purpose says it is the `predictor_v3` project-wide owner.
- Scope names calculator, Predictor, Trainer, ML/inverse-search, PyQt, and
  Tkinter.
- Detail/graph and validation policy include good general rules but mix in
  concrete current-project implementation constraints.
- Examples are useful but should clearly be examples, not scope boundaries.
- Adoption order names task-163, ISO Hong Kong, Tkinter smoke, PyQt retirement,
  and packaging decisions.

Recommendation:

- Make purpose portable: repeated structured input and result-output surface
  shaping for engineering/data tools.
- Generalize role names in principle text: single-case immediate calculation,
  batch/model operation surfaces, detail/diagnostic surfaces.
- Keep calculator/Predictor/Trainer/ISO examples in an `Examples / Evidence`
  section.
- Move current-project rollout/adoption order out of principle body or relabel
  as current-project binding notes.

Include in 230D: Yes.

### `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`

Neutralization need: Medium.

Findings:

- Purpose is already toolkit-agnostic.
- Scope lists concrete implementations: current Tkinter calculator, future C#
  WPF shells, PySide/PyQt, Web.
- It records lessons from Tkinter calculator geometry work, which is useful
  evidence but can read as scope if left in the purpose/scope body.
- `WPF Implementation Guide` is an adapter-like section inside a portable
  policy document.

Recommendation:

- Keep the placement modes, nested notebook/dynamic refit policy, multi-monitor
  rules, scroll policy, manual resize policy, and acceptance checklist.
- Reword scope to interface-neutral terms.
- Move concrete implementation names into an `Observed Examples / Adapter
  Notes` section.
- Decide in 230D whether the WPF guide stays as adapter note or becomes a
  future adapter-doc candidate. Do not expand it.

Include in 230D: Yes, but as a smaller scope/example wording pass.

## Adapter Exclusion Judgment

Adapter documents are not neutral principle documents. Specific toolkit names
are expected and should remain:

- `PYQT_TABLE_IMPLEMENTATION.md`
- `TKINTER_TABLE_ADAPTER.md`

The only adapter risk to watch is whether an adapter claims permission to
change product UX or override portable contracts. The current audit did not
identify a blocker requiring adapter edits in 230D. Adapter neutralization is
excluded.

## ACTIVE_DOCUMENTS Impact

Potential sync candidates for 230D:

- `04_VISUAL_DESIGN_ARCHITECTURE.md` role currently says
  `predictor_v3 project-wide visual architecture SSOT`; after neutralization it
  should likely say portable/common visual design architecture owner.
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` role currently says
  `predictor_v3 project-wide repeated-input matrix and result-summary surface
  rules`; after neutralization it should likely say portable/common repeated
  input matrix and result surface owner.
- `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` role is already acceptable, but
  outbound wording may be generalized from named frameworks to interface-shell
  geometry implementations.
- Adapter rows should keep toolkit-specific names.

No `ACTIVE_DOCUMENTS.md` changes were made in this audit because the actual
owner wording should follow the 230D document edits.

## 230D Implementation Slice Proposal

Recommended next task:

`230D — UI/UX portable-document neutralization first slice`

Include:

- neutralize `04_VISUAL_DESIGN_ARCHITECTURE.md` purpose/scope/adoption wording;
- neutralize `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` purpose/scope,
  principle body, examples/evidence split, and adoption order wording;
- lightly neutralize `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` scope and
  implementation-example wording;
- sync affected `ACTIVE_DOCUMENTS.md` role/outbound wording;
- update WORK_PLAN/project_log/report.

Exclude:

- adapter document neutralization;
- code changes;
- UI behavior changes;
- 07 policy behavior changes beyond wording/scope split;
- architecture boundary document rewrites;
- docs/designs changes;
- report lifecycle/archive movement.

## Excluded Scope

- No `docs/ui_ux` body changes in this audit.
- No adapter edits.
- No code or test changes.
- No architecture policy rewrite.
- No report lifecycle cleanup.

## Validation

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing soft warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: only expected work plan, project log, and report files
  changed before commit.
- `pytest`: not run; audit/report-only task.
- GUI smoke: not run; no UI code changes.

## Next Action

UI/UX portable-document neutralization first slice.

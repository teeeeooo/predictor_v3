# Arc 13.5A Feature Catalog Manager Correction Design

Date: 2026-07-02  
Target repo path: `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md`  
Repo basis: `teeeeooo/predictor_v3` main branch after Arc 13.5 closeout, remote main `2d2103e60b57f7f7859b35e0b0621014b2776cd8`

## 1. Purpose

Arc 13.5 implemented a safe Feature Catalog viewer/editor foundation, but the resulting scope is narrower than the intended user workflow.

The current implementation is closer to a limited metadata editor for an existing `config/ml/features.csv` file. The intended workflow is a GUI-based Feature Catalog Manager where the user can add, delete, duplicate, edit, validate, and save ML feature definitions without manually editing CSV or memorizing internal allowlist values.

This document fixes the direction before the codebase grows further.

## 2. Current State Summary

Arc 13.5 completed these pieces:

- Feature Catalog tab in Train shell
- read-only/viewer style table foundation
- validation display
- UTF-8-SIG export
- editable/save workflow for a limited set of columns
- canonical UTF-8 save with validation
- docs closeout and tests

Current limitations:

- Users cannot add new feature rows from GUI.
- Users cannot delete feature rows from GUI.
- Users cannot duplicate an existing feature row.
- Many values are plain text fields even when the allowed values are fixed.
- GUI headers expose developer-facing names such as `ml_name`, `ui_key`, `zero_fill_policy`, `one_hot_group`.
- Help/term explanation is missing.
- `feature_id` and `ml_name` are both exposed as if they are separate user concepts.
- CSV export currently risks exporting the last loaded snapshot rather than the currently edited table state.
- Dirty state is edit-flag based, not baseline-diff based.
- Save updates `features.csv`, but there is no complete live schema refresh path for already-open Predict table UI.
- Model artifact compatibility with changed catalog is not yet strongly guarded.

## 3. Corrected Product Goal

The corrected target is:

- The user manages Feature Catalog entries from GUI.
- The user can add, delete, duplicate, and edit features safely.
- The GUI presents user-friendly column names and dropdowns instead of raw internal values.
- The user can open Help to understand terms, allowed values, and feature type behavior.
- Save is blocked unless catalog validation and project consistency validation pass.
- Saving the catalog can refresh schema-dependent UI surfaces or clearly require restart where live refresh is not yet supported.
- Catalog changes that affect ML features are treated as requiring retraining and model compatibility confirmation.

## 4. Architecture Direction

Keep the Arc 13.5 boundary direction:

- UI panel: rendering, user interaction, dialogs only
- Controller: thin boundary between UI and application service
- Application service: catalog workflow, validation orchestration, DTO conversion, save/export operations
- Adapter/file writer: CSV I/O, UTF-8-SIG export, canonical UTF-8 safe write
- Core ML catalog: catalog data model, loader, validation, projection helpers
- Predictor schema projection: consume catalog and project table columns
- Predict/Train UI shell: react to schema refresh events, do not own catalog business rules

Do not let UI directly parse/write `features.csv`.  
Do not put PySide6 dependencies inside `core/ml`.  
Do not bypass catalog validation for GUI save.

## 5. Important Design Decision: Remove `feature_id`

### 5.1 Current finding

GitHub main audit showed that `feature_id` is currently not a meaningful runtime projection key.

Runtime paths primarily use `ml_name`:

- `BASE_FEATURES`
- `DERIVED_FEATURES`
- `TARGETS`
- predictor `ml_feature`
- predictor `ml_target`
- one-hot feature names
- zero-fill policy map keys
- training header contract validation
- model registry target/rule validation

`feature_id` currently mainly does two things:

- active-row uniqueness validation
- validation error prefix such as `feature_id=...`

Both can be replaced by `ml_name`, with order/line used for additional error location.

### 5.2 Decision

Remove `feature_id` from the Feature Catalog schema before expanding Feature Manager UI.

New identity rule:

- `ml_name` is the catalog row primary identity.
- `ml_name` is the raw training data column name and internal ML feature/target name.
- active rows with non-empty `ml_name` must remain unique.
- validation messages should identify rows using `ml_name`, and include order/line context where useful.

Keep `ui_key` because it has a different responsibility:

- `ui_key` is the UI/table column key.
- It may be auto-generated from `ml_name` for new rows.
- It may be hidden or advanced in GUI for most users.

### 5.3 Expected schema after removal

Canonical `features.csv` headers should become:

- `order`
- `ml_name`
- `role`
- `ui_key`
- `label`
- `source`
- `mapping_key`
- `one_hot_group`
- `zero_fill_policy`
- `active`
- `notes`

No `feature_id` column.

## 6. User-Friendly GUI Column Names

Canonical CSV headers remain English/internal. GUI display names must be user-friendly.

Recommended display mapping:

| Canonical field | GUI display name | Notes |
|---|---|---|
| `order` | 순서 | Usually auto-assigned |
| `ml_name` | 학습 데이터 컬럼명 | Primary catalog identity |
| `role` | Feature 유형 | Dropdown |
| `ui_key` | 화면 항목 키 | Usually auto-generated or advanced |
| `label` | 화면 표시명 | User-facing table header |
| `source` | 데이터 출처 | Dropdown, for auto features |
| `mapping_key` | 매핑 키 | Dropdown/filter by source where possible |
| `one_hot_group` | One-hot 그룹 | Dropdown |
| `zero_fill_policy` | 누락값 처리 | Dropdown |
| `active` | 사용 여부 | Checkbox/dropdown |
| `notes` | 메모 | Free text |

## 7. Dropdown / Allowlist UX

The user should not memorize allowed values.

Dropdown candidates should be provided by application service DTOs, not hard-coded inside the UI widget.

Minimum dropdown fields:

| Field | Source of allowed values |
|---|---|
| `role` | catalog validation owner, e.g. `input`, `auto`, `result`, `derived`, `one_hot`, `hidden` |
| `active` | `true`, `false` or checkbox |
| `zero_fill_policy` | `disallow`, `mode_missing_allowed` |
| `source` | known source names used by autofill/mapping logic |
| `mapping_key` | known mapping keys, preferably filtered by selected source |
| `one_hot_group` | existing catalog groups plus allowed/new group policy |

Dropdowns must not bypass validation. They are UX aids; validation remains authoritative.

## 8. Help Dialog Requirements

Add a Help button for Feature Catalog Manager.

Help content should explain:

- What a Feature Catalog row is
- Meaning of `ml_name`
- Meaning of `ui_key`
- Meaning of each feature role
- Required fields by role
- Allowlist values and when to use them
- One-hot group concept
- Zero-fill policy concept
- Why some catalog changes require model retraining
- Example: add simple input feature
- Example: add auto/mapping feature
- Example: add one-hot category
- Example validation errors and how to fix them

Help should be readable by HVAC engineers, not only by developers.

## 9. Feature Types and Expected Behavior

| Role | GUI add support | UI table impact | Training impact | Extra requirement |
|---|---:|---|---|---|
| `input` | Yes | Adds user input column if `ui_key` exists | Training data header required | Numeric input expected |
| `auto` | Yes | Adds auto-filled column if `ui_key` exists | Training data header required | `source` and `mapping_key` required |
| `result` | Yes, but advanced | Adds read-only result column | Target/model registry impact | May require registry update |
| `one_hot` | Yes, category-level first | Usually no direct table column | Training data header required | Existing one-hot group required unless new group workflow exists |
| `derived` | Limited/advanced | No direct table column | Derived feature calculation required | Formula/code owner needed |
| `hidden` | Advanced | Hidden from UI | Internal ML feature only | Use carefully |

Initial implementation should prefer simple, safe workflows:

- input feature add
- auto feature add
- one-hot category add to existing group
- duplicate existing row
- delete selected row

New derived formula creation should not be treated as a simple GUI-only operation because preprocessing logic is code-owned.

## 10. Add / Delete / Duplicate Workflow

### Add feature

Preferred UX: dialog-based add, not raw empty row insertion.

Dialog fields:

- Feature 유형
- 학습 데이터 컬럼명
- 화면 표시명
- 데이터 출처, if role is `auto`
- 매핑 키, if role is `auto`
- One-hot 그룹, if role is `one_hot`
- 누락값 처리
- 사용 여부
- 메모

Auto-generated fields:

- `ui_key` from `ml_name` for UI-visible roles, with collision handling
- `order` as next stable order slot

### Duplicate feature

Duplicate selected row and require user to change at least:

- `ml_name`
- `ui_key`, if UI-visible
- `label`

Duplicated row must not save if it violates uniqueness validation.

### Delete feature

Delete selected row with confirmation.

Deletion should operate on draft table state first. Actual file change happens only on save.

For active rows that are referenced by model registry or predictor schema, validation should block save or show clear errors.

## 11. Save / Export / Dirty State

### Save

Save flow should remain validation-gated:

- table records to domain rows
- conversion validation
- catalog-only validation
- project consistency validation
- canonical UTF-8 safe write through temp file and replace
- reload saved catalog
- return save result

### Export

CSV export should export current table state, not stale loaded snapshot.

Expected behavior:

- If user edited table but did not save, export should include pending edits.
- Export file remains UTF-8-SIG for Excel compatibility.
- Export does not mutate canonical `features.csv`.

### Dirty state

Dirty state should be baseline-diff based:

- On load/save, capture baseline records.
- On edit/undo/add/delete/duplicate, compare current records to baseline.
- Dirty is true only when current table state differs from baseline.

## 12. Schema Refresh after Catalog Save

Catalog save should eventually affect schema-driven UI surfaces.

Current system already has partial catalog-driven projection:

- `core/predictor_schema/columns.py` loads catalog and builds `COLUMNS` at import time.
- `predictor_columns_projection()` projects active `input`, `auto`, and `result` rows into predictor columns.
- Training header guard validates raw training headers against catalog `ml_name`.
- Inference uses catalog-derived base features, targets, one-hot groups, and zero-fill policies.

Missing part:

- Live refresh after GUI save.

Target flow:

- Feature Catalog Manager save succeeds
- Catalog is reloaded
- Predictor schema projection is rebuilt
- Train/Predict shell receives schema-changed event
- Predict table model resets columns
- Existing row data is migrated where keys still match
- New columns appear blank/default
- Removed columns are dropped from visible table state
- User sees a clear status message

Initial implementation may choose restart-required if live refresh is too broad, but the UI must be honest:

- “Catalog saved. Restart app to apply table schema changes.”

Longer-term target is live refresh.

## 13. Model Compatibility and Retraining

Catalog changes may invalidate existing `model.pkl`.

Important rule:

- Changing active `ml_name`, `role`, `one_hot_group`, or `zero_fill_policy`, or
  toggling `active`, can require model retraining.
- Changing `label`, `notes`, `order`, or `ui_key` does not change the model
  artifact compatibility fingerprint.
- `source` and `mapping_key` are UI/input mapping concerns and are excluded from
  the model artifact compatibility fingerprint. A separate UI schema/apply
  fingerprint can be considered later, but is not implemented in this slice.

Recommended guard:

- Compute catalog fingerprint/hash from the active-row projected ML contract.
- Store catalog fingerprint in model artifact when training completes.
- When loading model for prediction, compare model artifact fingerprint with current catalog fingerprint.
- If mismatch, block or warn clearly: model was trained with a different Feature Catalog and retraining is required.

This should be handled as a separate slice because it touches training artifact contract.

## 14. Implementation Slice Plan

### Slice 0: Identity simplification foundation

Goal:

- Remove `feature_id` from catalog schema and code.
- Use `ml_name` as catalog row identity.
- Update validation messages and tests.
- Update docs to remove `feature_id` concept.

Allowed modifications:

- `config/ml/features.csv`
- `core/ml/feature_catalog.py`
- `core/ml/feature_catalog_validation.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/application/feature_catalog/service.py`
- focused tests
- relevant docs/design notes

Do not do:

- Add/delete GUI implementation
- Dropdown/help UI implementation
- Schema refresh implementation
- Model artifact hash implementation

Validation:

- focused feature catalog tests
- focused train feature catalog app tests
- focused predictor schema tests if affected
- compileall
- git diff --check

Status note (2026-07-02): Slice 0 implementation removed the catalog `feature_id` field from schema, validation, and train DTO paths. `ml_name` is now the catalog row identity for validation messages.

### Slice 1: Feature Manager UX foundation

Goal:

- User-friendly GUI headers.
- Dropdown delegates for allowlist fields.
- Help dialog.
- Export current table state.
- Dirty state baseline diff.

Do not do:

- Add/delete/duplicate feature rows yet.
- Schema live refresh yet.
- Model hash yet.

Status note (2026-07-02): Slice 1 implementation added user-friendly table headers, DTO-provided dropdown options, Help dialog, current-table export, and baseline-diff dirty state.

### Slice 2: Add / Delete / Duplicate feature rows

Goal:

- Add Feature dialog.
- Duplicate selected row.
- Delete selected row with confirmation.
- Auto-generate `ui_key` and `order`.
- Preserve validation-gated save.

Do not do:

- Derived formula editor.
- New one-hot group UI unless explicitly scoped.
- Model artifact compatibility implementation.

Status note (2026-07-02): Slice 2 implementation added Add Feature dialog, Duplicate, Delete with confirmation, generated `order`/`ui_key`, and draft-state validation-gated save.

### Slice 3: Schema refresh and apply behavior

Goal:

- Define and implement post-save schema refresh path.
- At minimum, show restart-required message if live refresh is not safely contained.
- Prefer live refresh if current shell/table model boundary supports it without broad refactor.

Do not do:

- Broad Predict UI rewrite.
- Unrelated table UX changes.

Status note (2026-07-02): Slice 3 implementation chose the restart-required path and surfaces the post-save schema apply message.

### Slice 4: Model compatibility guard

Goal:

- Compute catalog fingerprint.
- Store fingerprint in training artifact.
- Compare on model load.
- Show retraining-required state or block incompatible prediction.

Do not do:

- ML algorithm changes.
- Training quality/tuning changes.

Status note (2026-07-02): Slice 4 implementation stores Feature Catalog fingerprint metadata in real and DEV artifacts and blocks missing/mismatched artifacts at model load.

Status note (2026-07-03): Arc 13.5A narrowed the model compatibility fingerprint
to active-row ML contract fields: `ml_name`, `role`, `one_hot_group`, and
`zero_fill_policy`. `active` changes compatibility by row inclusion/exclusion,
not by being stored in each payload row.

### Slice 5: Common table helper cleanup

Goal:

- Move generic clipboard/undo helpers out of `apps.predict.ui.tables` into common UI helper ownership.
- Train and Predict tables use the common helper.

Do not do:

- Feature Manager behavior changes in this slice.

Status note (2026-07-02): Slice 5 moved generic clipboard/undo table helpers to `apps.common.ui.tables` and updated Train/Predict imports.

### Closeout

Goal:

- Update workflow docs.
- Update result reports.
- Record validation and manual smoke status.
- Mark next action clearly.

## 15. Manual Smoke Checklist

Manual smoke should cover:

- Open Train app and Feature Catalog tab.
- Confirm user-friendly headers.
- Confirm dropdown values are available.
- Open Help and verify explanations are understandable.
- Add input feature in draft state.
- Duplicate feature and verify validation catches duplicate `ml_name` or `ui_key`.
- Delete draft row.
- Export current dirty state and confirm pending edits are included.
- Save valid change.
- Save invalid change and confirm file is not mutated.
- Confirm predict schema behavior after save or restart-required message.
- Confirm model retrain required message when catalog/model fingerprint mismatch exists, once implemented.

## 16. Open Questions

- Should `ui_key` be visible by default or hidden under advanced mode?
- Should adding `result` rows require editing model registry in the same workflow, or should GUI block result add until registry support is designed?
- Should new one-hot groups be supported immediately, or only new categories inside existing groups?
- Should live schema refresh be implemented now, or should first version display restart-required status?
- What exact source owns valid `source` and `mapping_key` allowlists?

## 17. Recommended Next Action

Next: Arc 13.5A complete; run manual desktop smoke on a local GUI session when available, then choose the next project slice.

Completed implementation covered Slice 1 through Slice 5 in sequence. Remaining open questions are product/design decisions for later work, not blockers for this correction arc.

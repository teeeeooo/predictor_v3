# Split Skills Patterns

## Goal

Read `skills_devide_plan.md`, split the sections from `data/skills.md` into the appropriate owner documents, move the original file to `docs/archive/skills_v2_patterns.md`, and avoid content loss.

## Scope

- Preserve the raw `data/skills.md` content by moving it to `docs/archive/skills_v2_patterns.md`.
- Place reusable UI, ML feature, ML safety, registry, artifact, and test-harness guidance in the owner docs identified by the plan.
- Record the migration result in Markdown.

## Changed Files

- `docs/archive/skills_v2_patterns.md`: moved original `data/skills.md` here with 100% rename preservation.
- `docs/architecture/project_architecture.md`: added UI delegate/paste/autofill guardrails, dropdown target mapping, MODEL_REGISTRY, model artifact, and V2 deprecated-pattern notes.
- `docs/knowledge/hvac_ml_feature_engineering.md`: added XGBoost/RFE DataFrame-native feature-selection pattern and candidate/selected snapshot expectations.
- `docs/knowledge/hvac_ml_data_quality.md`: added ML safety gates, preprocess/feature/leakage checks, layered test harness, optimization harness, and snapshot management rules.
- `project_log.md`: recorded that `data/skills.md` is now an archived V2 pattern source and owner docs hold active reusable guidance.
- `result_reports/active/018_split-skills-patterns.md`: this compact result report.

## Section Mapping / Omission Audit

| Original section | Owner placement |
| --- | --- |
| PyQt5 1-click dropdown delegate | `docs/architecture/project_architecture.md` UI Model/View Guardrails; raw V2 code kept in archive |
| XGBoost + Pandas Native RFE pipeline | `docs/knowledge/hvac_ml_feature_engineering.md` XGBoost RFE Feature Selection Pattern |
| SSOT dropdown-target mapping | `docs/architecture/project_architecture.md` COLUMNS autofill structure |
| Cascading autofill and UI state lock | `docs/architecture/project_architecture.md` COLUMNS autofill structure and UI guardrails |
| ML safety patterns | `docs/knowledge/hvac_ml_data_quality.md` ML Safety Gates |
| MODEL_REGISTRY pattern | `docs/architecture/project_architecture.md` MODEL_REGISTRY extensibility pattern |
| Test harness pattern | `docs/knowledge/hvac_ml_data_quality.md` Test Harness Strategy |

## Verification

- `shasum -a 256`: original `data/skills.md` and moved `docs/archive/skills_v2_patterns.md` both matched `9c072a1820dd0350045bbd95bbba21620bd3b0b53eaaffc40fe3b6d274e048a7`.
- Archive section count: 7 legacy sections found in `docs/archive/skills_v2_patterns.md`.
- `git diff --check`: OK.
- `git diff --name-status HEAD`: confirmed modified owner docs plus `R100 data/skills.md -> docs/archive/skills_v2_patterns.md`.
- Keyword audit confirmed owner docs contain the expected terms for `QTimer`, paste handling, `DROPDOWN_TARGET`, `ml_feature`, cascading autofill, `MODEL_REGISTRY`, `model.pkl`, `OptimalModel`, SHAP, XGBoost/RFE/RFECV, `feature_names_in_`, candidate/selected snapshots, `preprocess_version`, feature freeze, leakage hard gate, Optuna, and optimization harness.
- Runtime tests were not run because this was documentation/archive migration only.

## Known Risks

- The archive preserves V2 raw code examples, including deprecated `QTableWidget` patterns. Active guidance points readers to `QTableView` / `QAbstractTableModel` / `QStyledItemDelegate` instead.
- The branch already had two unpushed `temporary commit` commits before this task, so pushing this task would also push those pre-existing commits.

## Commit / Push

- Source commit: `45958c7 docs: split skills patterns into owner docs`.
- Report commit: committed separately after source commit.
- Push: not performed yet because the branch was already ahead of `origin/main` by pre-existing commits before this task.

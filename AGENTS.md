# predictor_v3 Agent Rules

This file is the always-on repository overlay. Global execution behavior is owned by the deployed user-level Codex `AGENTS.md`; this file keeps predictor_v3 invariants and routing only.

## Repository invariants

- Keep `app_train.py` and `app_predict.py` separate thin entrypoints.
- Predict inference stays in `core/ml/inference.py` and shared inference runtime; do not import training/tuning-only paths into Predict.
- Canonical Data Definition/runtime generation owns Feature/Target association and target-level policy. `COLUMNS`, `MODEL_REGISTRY`, and generated catalogs are compatibility projections, not writable SSOTs.
- Calculator implementations remain pure Python without `numpy` or `pandas`.
- Do not restore retired `calculate_hspf2_v2()` or historical fallback engines.
- Preserve Cooling/Heating model independence, `feature_names_in_`, monotone constraints, and physical constraints.
- Keep region config, HW candidate input, ML feature schema, calculator result schema, and UI table/export schema separate.
- Public functions, JSON keys, diagnostics, persisted contracts, and accepted goldens change only when the task explicitly changes that contract.

## Routing

- Calculator/standards/config/goldens: `.agents/skills/calculator/SKILL.md`.
- Train/Predict/ML/runtime Target authority: `.agents/skills/ml-predictor/SKILL.md`.
- Packaging/deployment build: `.agents/skills/packaging/SKILL.md`.
- Predictor UI ownership starts at `docs/ui_ux/README.md`; use the global `desktop-table-ui` or `desktop-window-lifecycle` Skill when the matching reusable interaction/lifecycle contract applies.
- Design interrogation/stress-testing uses the global `grill-me` Skill when its guarded implicit trigger or explicit invocation applies.
- When the durable owner is unclear, use `ACTIVE_DOCUMENTS.md` and stop once the relevant owner and focused evidence are known.

## Architecture and recall

Before adding or moving responsibility, identify the existing Model / Service-or-Controller / Shell-or-Adapter / View / Policy owner. Use `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` when a task changes a public/schema/registry/resolver boundary, cross-layer responsibility, reusable cross-surface mechanism, or persisted/runtime ownership.

For past-dependent work, follow `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`: start from the compact memory seed, then one relevant decision/failure record, then verify current truth at the active owner. Historical result records and logs are evidence, not active policy.

## Mechanical governance

- Staged objective checks: `docs/agent_workflows/AGENT_CHANGE_GATES.md`.
- Document owner/lifecycle sync: `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`.
- Region config edits: `data/region_configs/REGION_CONFIG_RULES.md`.
- Standard documentation structure: `docs/DOCS_GUIDELINES.md` when that structure actually changes.

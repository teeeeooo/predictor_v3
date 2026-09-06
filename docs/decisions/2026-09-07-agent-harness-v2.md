# Decision — Agent Harness V2

## Decision

predictor_v3 uses the user-level `operating-envelope` harness for generic execution behavior and reusable global Skills. The repository keeps only predictor-specific invariants, owner routing, domain Skills, focused mechanical guards, and project knowledge.

The mandatory/conditional Result Record workflow is retired as an active change requirement. Existing Result Records and `REPORT_INDEX.md` remain historical evidence. The compact project memory seed remains the hot recall index, with selective decision/failure records for durable “why” and “do not repeat” knowledge.

Repository-local `grill-me` and `ui-surface` Skills are retired. Design interrogation/stress-testing is owned by the global upstream-derived `grill-me` Skill; reusable table/window lifecycle behavior is owned by the global `desktop-table-ui` and `desktop-window-lifecycle` Skills. Predictor-specific UI ownership remains under `docs/ui_ux/`.

## Why

GPT-6 Astra is instruction-sensitive. Repeating generic autonomy, approval, verification, UI interaction, and memory ceremony across always-on and conditional surfaces increases conflict risk and context cost. The previous Result Record/Memory Review coupling also turned durable-memory judgment into routine write ceremony.

## Rejected alternatives

- Keep Result Records as the default durable artifact for architecture/harness/schema work: rejected because Git + current owner docs + selective decision/failure records cover the durable need with less ceremony.
- Keep `ui-surface` as a routing-only Skill: rejected because its reusable behavior moved global and the remaining predictor routing fits `AGENTS.md` plus `docs/ui_ux/README.md`.
- Delete the memory seed: rejected because it provides a high-value bounded recall index for a long-running project.

## Current owners

- shared harness: `teeeeooo/operating-envelope`;
- predictor repository overlay: `AGENTS.md`;
- recall/write policy: `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`;
- mechanical guard: `docs/agent_workflows/AGENT_CHANGE_GATES.md`;
- UI owner root: `docs/ui_ux/README.md`.

## Revisit conditions

Revisit if bounded recall routinely fails to recover needed decisions, if global Skills cannot express repeated cross-repo behavior without product leakage, or if a concrete compliance/release requirement needs a stronger durable change artifact than Git + owner/decision records.

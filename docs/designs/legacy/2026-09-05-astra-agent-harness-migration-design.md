# Design Gate — Astra Agent Harness Migration

## Goal

Refactor predictor_v3 agent instructions for GPT-6 Astra-era Codex behavior without changing product/runtime code. Reduce always-on instruction surface, retire Engineering Workflow for new work, and move project-specific task procedure into repository-local Skills.

## Context

OpenAI's current Astra guidance states that the model follows long instructions strongly but can pause early when Skill/instruction guidance conflicts. Current Codex Skill guidance supports progressive disclosure from `$REPO_ROOT/.agents/skills`, with optional explicit-only invocation policy in `agents/openai.yaml`.

Repository audit found a sound owner model but repeated generic workflow policy across `AGENTS.md`, the task router, workflow docs, architecture docs, and active memory. `grill-me` also forced repeated clarification and was implicitly invokable.

## Confirmed Decisions

- Engineering Workflow, its Worker/Auditor/Orchestrator roles, Lane A-D model, and Build-Gate-Close ceremony are retired for new predictor_v3 work.
- Historical logs, records, archived memory, and legacy designs that describe those mechanisms remain historical evidence and are not rewritten.
- `AGENTS.md` becomes the only always-on repository execution contract.
- Calculator, ML/Predictor, UI, and packaging procedure becomes repository-local Skills under `.agents/skills/`.
- `grill-me` remains repository-local but is explicit-only and asks only decision-bearing questions.
- `ACTIVE_DOCUMENTS.md` remains the durable owner discovery map.
- Change gates, document lifecycle, Result Records, and memory remain governance documents rather than Skills.
## Boundary Decision

| Item | Owner after migration | Reason |
| --- | --- | --- |
| Always-on execution posture and hard boundaries | `AGENTS.md` | Keep persistent context small and unambiguous |
| Task-specific calculator procedure | `.agents/skills/calculator/SKILL.md` | Progressive project-local loading |
| Task-specific ML/Predictor procedure | `.agents/skills/ml-predictor/SKILL.md` | Progressive project-local loading |
| Task-specific UI procedure | `.agents/skills/ui-surface/SKILL.md` | Route to detailed `docs/ui_ux/` owners instead of duplicating them |
| Packaging procedure | `.agents/skills/packaging/SKILL.md` | Load only for packaging work |
| Design interrogation | `.agents/skills/grill-me/SKILL.md` | Explicit-only bounded uncertainty resolution |
| Durable owner discovery | `ACTIVE_DOCUMENTS.md` | Repository topology, not execution procedure |
| Mechanical enforcement | `AGENT_CHANGE_GATES.md` | Describes checker/hook contract |
| Record/memory/document lifecycle | governance docs | Persisted repository semantics, not task procedure |

## Execution Semantics

- Inspect repository evidence instead of asking the user for repository-answerable facts.
- Resolve routine ambiguity conservatively and ask only when different answers materially change behavior, public/persisted compatibility, destructive scope, authority, or acceptance.
- Once authorized, continue to the requested end state unless a real blocker or unapproved material boundary is found.
- Verification starts with the narrowest meaningful owner evidence and expands or repeats only after invalidation, failure, or unresolved acceptance evidence.
- User instructions take precedence over repository-local Skill guidance.
## Compatibility And Migration

Slice 1 moved the four task workflows to repository-local Skills, rewrote `AGENTS.md`, made `grill-me` explicit-only, removed Engineering Workflow authority from current active guidance, and synchronized owner references/memory.

Slice 2 verified that no current active owner depends on `AGENT_TASK_ROUTER.md` and retires that compatibility pointer. Historical references do not block retirement and remain evidence of the pre-cutover harness.

## Required Validation

- Skill discovery paths and frontmatter are valid and `grill-me/agents/openai.yaml` disables implicit invocation.
- Active guidance has no current Engineering Workflow/Lane/Worker/Auditor/Orchestrator authority dependency.
- Historical evidence remains unchanged except current indexes/owner descriptions that must point to the new system.
- No production Python/test/runtime behavior changes occur.
- The agent change gate, documentation/reference checks, and `git diff --check` pass for the harness change.
- Result Record/index/memory coupling remains valid.

## Non-goals

- No product, calculator, ML, UI runtime, schema, persistence, formula, golden, packaging output, or public API change.
- No global/user-level Skill installation.
- No new fixed Worker/Auditor role framework or replacement lane taxonomy.
- No historical Result Record, archived memory, legacy design, or archived project-log rewrite.

## Completion State

Both migration slices are complete when the router deletion, active-reference search, focused harness tests, staged change gate, and diff checks pass. Future agent-harness work starts from `AGENTS.md`, repository-local Skills, `ACTIVE_DOCUMENTS.md`, and the matching governance/owner documents.
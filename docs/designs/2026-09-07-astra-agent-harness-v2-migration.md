# Astra Agent Harness V2 Migration

## Goal

Apply the shared V2 architecture from `operating-envelope` to predictor_v3 without changing product/runtime behavior.

## Repository delta

- shrink root `AGENTS.md` to predictor-specific invariants and routing;
- retain calculator, ML/Predictor, and packaging repo Skills;
- retire repo-local `grill-me` and `ui-surface`; use the upstream-derived global `grill-me` for design interrogation and global UI Skills for reusable table/window behavior;
- retire active Result Record creation/index/memory coupling;
- retain `project_memory_seed.md` as the compact recall index;
- add selective `docs/decisions/` and `docs/failures/` warm memory;
- keep historical Result Records and indexes as cold evidence;
- simplify the staged change checker to objective failures plus warning-first structure signals.

## Mechanical checker contract

Hard failures remain staged whitespace, Python syntax, Phase 1 UI literal policy, and optional manifest scope violations. Source size, class count, hotspot growth, and structural reuse are warnings. The optional Git-local manifest owns only literal staged-path scope and an approved UI-literal exemption.

## Validation

Use focused harness/checker/hook tests, active-reference searches, Skill discovery checks, `git diff --check`, and a fresh Codex `gpt-reserve --ephemeral` overlay probe. Product tests are not required because no product/runtime behavior changes.

## Non-goals

No calculator formulas, ML behavior, UI runtime, schema, persistence, packaging output, public API, or golden changes. Historical evidence bodies are not rewritten merely to match current policy.

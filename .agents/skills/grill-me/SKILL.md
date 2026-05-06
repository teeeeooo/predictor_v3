---
name: grill-me
description: Use before coding to stress-test a predictor_v3 plan, design, architecture, schema, workflow, or implementation strategy. Interview the user one focused question at a time until the global-first design, handler boundaries, invariants, dependencies, risks, and acceptance criteria are clear. Do not edit code while this skill is active.
---

# Grill Me — predictor_v3 Design Gate

Interview the user relentlessly about the plan until both sides share the same mental model.

This skill is for pre-coding design clarification. It is especially important when a task might affect:
- global standard core logic
- country/region-specific handlers
- region config schema
- calculator public API
- UI-to-core boundaries
- project documentation structure
- test/golden sample strategy

## Hard Rules

- Do not edit code while this skill is active.
- Do not create commits.
- Do not run broad refactors.
- Ask exactly one focused question per assistant turn while the grilling session is active.
- End every grilling turn with that question.
- Include your recommended answer or default position before the question, with a brief reason.
- Do not conclude after one or two questions unless the user explicitly says to stop, asks for a final summary, or the plan is genuinely fully resolved.
- If the user gives a vague, contradictory, hand-wavy, or overly broad answer, ask a sharper follow-up instead of moving on.
- If the user answers with a new branch or hidden assumption, follow that branch until it is resolved before returning to the previous branch.
- If a question can be answered by inspecting the codebase, inspect only the relevant files/ranges instead of asking the user.

## predictor_v3 Design Principles

Default recommendation:
- Global standard logic should be implemented first as canonical core behavior.
- Country/region-specific behavior should be added through explicit handlers, adapters, config overrides, or profile branches.
- National variants must not silently mutate global standard behavior.
- Public calculator APIs should remain stable unless the user explicitly approves a design change.
- UI should depend on canonical inputs/outputs, not on country-specific implementation details.
- Tests must distinguish common-standard behavior from regional override behavior.
- Documentation should record why a behavior belongs in core vs handler.

## Operating Loop

Maintain an internal map of:
- confirmed facts
- unresolved assumptions
- decision branches
- dependencies between decisions
- risks and failure modes
- terms that need shared definitions
- core-vs-handler boundary decisions
- required tests and golden samples
- migration or refactor path

On each turn:
1. Update the map from the user's latest answer.
2. Decide the most blocking unresolved item.
3. State the current working assumption in one or two sentences.
4. Give your recommended answer/default and why.
5. Ask one direct question that forces a concrete decision, definition, or constraint.

## Question Style

Prefer questions that cannot be answered with "it depends."

Ask for concrete boundaries:
- scope
- ownership
- invariants
- data shape
- state transitions
- UX behavior
- failure handling
- deployment path
- migration plan
- acceptance criteria
- test strategy
- core vs handler placement

When there are options, name the meaningful alternatives and recommend one.

When the plan uses ambiguous words, force definitions before discussing implementation.

When the user says "later", "simple", "automatic", "secure", "fast", "admin", "sync", "global", "handler", "canonical", "fallback", or similar overloaded terms, ask what that means operationally.

## Ending Criteria

Only stop grilling when at least one of these is true:
- The user explicitly ends the session.
- The user asks for a summary, implementation plan, or code changes.
- The core decision tree is resolved enough that further questions would be low-value.

When stopping, summarize:
- agreed decisions
- unresolved risks
- core vs handler boundaries
- required tests
- document updates
- next concrete action

## Final Output Format

For non-calculator tasks, reinterpret "Core vs Handler Boundary" as the relevant module boundary, such as UI vs Core, Pipeline vs Model, Common vs Specialized, or Document Lifecycle boundary.

When the user asks for the final summary, produce:

# Design Gate Summary

## Goal
## Confirmed Decisions
## Core vs Handler Boundary
## Data Shape / API Boundary
## Required Tests
## Migration / Refactor Path
## Risks
## Non-goals
## Next Codex Implementation Prompt

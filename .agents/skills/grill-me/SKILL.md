---
name: grill-me
description: Explicit-only predictor_v3 design interview for resolving decision-bearing uncertainty before implementation. Use only when the user invokes this skill or directly asks for a design interrogation.
---

# Grill Me — predictor_v3 Design Gate

Use this skill only when explicitly invoked. The user's explicit task takes precedence over this skill.

## Purpose

Resolve design uncertainty that would materially change architecture, public or persisted contracts, compatibility, domain behavior, or acceptance. Do not turn routine implementation uncertainty into a question loop.

## Decision gate

Before asking the user:

1. Inspect the relevant repository owner if the answer can be recovered from current source or documentation.
2. If different answers would not materially change behavior, compatibility, authority, destructive scope, or acceptance, choose the most conservative reasonable default and continue.
3. Ask only when the unresolved choice is genuinely decision-bearing and cannot be resolved from repository evidence.
4. Ask one focused question at a time when a question is necessary.

Do not ask questions merely to satisfy a process, fill a checklist, or confirm an already-specified boundary.

## predictor_v3 design defaults

- Put common standard behavior in the canonical common owner and region/product specialization behind explicit handlers, adapters, profiles, or config.
- Do not silently mutate global-standard behavior for a national variant.
- Keep public calculator APIs stable unless the task explicitly changes them.
- Keep UI dependent on canonical inputs/outputs rather than specialized implementation details.
- Keep common behavior and specialized overrides separately testable.
- Preserve current Model/Service-or-Controller/Shell-or-Adapter/View/Policy ownership and dependency direction unless the design decision explicitly changes responsibility.

## When to stop

Stop the interview when the decision-bearing tree is resolved enough to implement, the user asks to stop, or the user asks for a summary/plan. Do not prolong the interview for low-value questions.

When stopping, summarize only the relevant decisions, unresolved risks, owner boundaries, required validation, migration path, non-goals, and next implementation action.

## Design persistence

Create a document under `docs/designs/YYYY-MM-DD-<task>.md` only when the user asks to persist the design or when the current task explicitly includes a governing Design Gate record. Otherwise return the summary in chat without creating a file.
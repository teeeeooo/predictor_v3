# Calculator Workflow

## Role

This document owns calculator, region, golden, smoke, validation, and Excel COM
reference workflow details. `AGENT_TASK_ROUTER.md` only routes here.

## Hard Boundaries

- Calculator implementations stay pure Python; do not introduce `numpy` or
  `pandas`.
- Do not modify `calculate_hspf2_v2()` / `calculate_hspf2()` unless the user
  explicitly asks.
- Keep ISO16358 common engine work centered on
  `core/calculators/standards/iso16358.py`; KS C 9306 special behavior belongs
  in `core/calculators/standards/ks_c9306.py`.
- Do not mix region config, HW candidate input, ML feature schema, UI table
  schema, or calculator result schema.
- Do not change public APIs, diagnostics schema, JSON keys, fixture/golden
  expected values, or function names without an approved reason.

## Owner Documents

- ISO16358 calculator work:
  `docs/iso16358/iso16358_dev_notes.md`
- KS C 9306 work:
  `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md`
  and `docs/iso16358/regions/ks_c_9306/ks_c_9306_notes.md`
- Region config edits:
  `data/region_configs/REGION_CONFIG_RULES.md`
- Architecture-sensitive profile/selector/schema changes:
  `docs/architecture/project_architecture.md`
- Refactor/phase guardrails when relevant:
  `docs/REFACTOR_PLAN.md`
- Excel COM reference packet work:
  `docs/iso16358/excel_com_runner_packet_protocol.md`

## Logic Change Flow

1. Decide whether the fix belongs in common engine logic, a profile/region
   adapter, config, or UI adapter.
2. Search for the target function/test first; read only the needed range.
3. Prefer common standard logic over region-specific hardcoding.
4. Keep production path and external-calculator compatibility path separate.
5. Compare branch trace, intermediate values, official formula mapping, and
   fixtures before changing expected values.
6. Treat external calculators, papers, knowledge docs, and LLM reports as
   evidence, not authority.
7. Report which evidence was used: formula, fixture, external calculator,
   reference trace, or config rule.

## Golden / Smoke / Validation Tests

- Golden tests defend confirmed calculation results.
- Smoke tests defend required keys, optional branches, region config behavior,
  and user-facing calculator calls.
- Validation tests defend input requirements, positive numeric constraints, and
  error boundaries.
- Use focused calculator validation for core/calculator logic, schema/public
  API, golden, fixture, or calculator route changes.
- Do not run calculator tests for docs-only or audit-only work that does not
  change calculator behavior, schema, fixtures, or expected values.
- Never distort calculation logic only to fit a test.
- Golden expected changes require official calculator evidence, hand
  calculation, or an already accepted project decision.

## Excel COM Packet Work

Use this gate only when the user mentions Excel COM, pywin32 runner, company PC
Excel, AS/NZS Energy Rating SEER calculator, original workbook reference,
chat_packet, full_dump, or case reference extraction.

Roles:

- ChatGPT: runner input packet design and chat_packet interpretation.
- Company PC runner: original Excel COM calculation, full_dump generation, and
  chat_packet generation.
- Codex: repo edits, tests, diff checks.
- User: runs company PC workflow and passes the chat_packet back.

Do not read the Excel COM protocol for ordinary calculator, UI, AHRI/EN/KS, or
ML work.

## Architecture-sensitive Calculator Work

Use an implementation/design split when adding or changing:

- calculator profile resolver;
- region config resolver;
- calculator registry / manifest / selector behavior;
- nested config or schema boundaries;
- ML output to calculator input adapters;
- calculator result schema normalization;
- UI/core/config/ML connections.

Prefer explicit selector/manifest/registry contracts over filename scanning.
Ambiguous selector combinations should fail fast.

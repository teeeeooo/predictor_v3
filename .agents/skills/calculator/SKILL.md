---
name: calculator
description: Use for predictor_v3 calculator formulas, standards, profiles, region configs, golden fixtures, calculator UI adapters, and calculator validation. Do not use for ML-only or packaging work.
---

# Calculator

Use this skill only for predictor_v3 calculator and standards work. The user's explicit task takes precedence over this skill.

## Hard boundaries

- Keep calculator implementations pure Python; do not introduce `numpy` or `pandas`.
- Do not restore retired `calculate_hspf2_v2()` or historical seasonal fallbacks.
- Keep ISO16358 common behavior in the common standard owner and KS C 9306 specialization in its own owner.
- Keep region config, HW candidate input, ML feature schema, UI table schema, and calculator result schema separate.
- Do not change public APIs, diagnostics keys, fixture/golden expectations, or function names unless the task explicitly requires that contract change.
- Preserve Appendix M SEER/HSPF and Appendix M1 SEER2/HSPF2 as physically separate owners.

## Owner routing

- ISO16358: `docs/iso16358/iso16358_dev_notes.md`.
- KS C 9306: `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md` and matching notes.
- Region config: `data/region_configs/REGION_CONFIG_RULES.md`.
- Shared calculator architecture: `docs/architecture/project_architecture.md`.
- Project-wide responsibility boundary: `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`.
- Calculator UI work also uses the repo-local `ui-surface` skill and matching `docs/ui_ux/` owner.

## Formula and golden changes

1. Decide whether the behavior belongs to the common standard engine, a profile/region owner, config, or a UI adapter.
2. Use official standard/formula evidence, accepted fixtures/goldens, or already-approved project decisions for expected-value changes.
3. Treat external calculators, papers, logs, and reports as evidence, not authority.
4. Prefer shared standard logic over region-specific hardcoding when the standard actually shares the rule.
5. Keep compatibility/reference-calculator paths separate from production behavior.

Golden tests defend confirmed numeric results. Smoke tests defend required keys, optional branches, profile/config behavior, and user-facing calculator calls. Validation tests defend input and error boundaries. Never distort production logic only to fit a test.

## Excel COM reference work

Use `docs/iso16358/excel_com_runner_packet_protocol.md` only when the task actually involves Excel COM, pywin32, company-PC Excel, an original workbook reference, `chat_packet`, `full_dump`, or case extraction. Do not load it for ordinary calculator work.

## Architecture trigger

Open the matching architecture owner before implementation when the task changes a profile/config resolver, calculator registry/manifest/selector, nested schema boundary, ML-to-calculator adapter, result normalization boundary, or UI/core/config connection. Prefer explicit selectors and fail fast on ambiguous combinations.

## Verification

Run the narrowest meaningful calculator tests for the changed owner first. Broaden or repeat passing validation only when a later change, failure, or unresolved evidence invalidates it. Use manual/platform validation only for behavior that cannot be adequately proven automatically.
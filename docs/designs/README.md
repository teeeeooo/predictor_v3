# Design Records

## Role

`docs/designs/` keeps only current governing, actively referenced, or future
unabsorbed design decisions. Design records are evidence, not active rule
owners; repeated rules belong in their architecture, repository-local Skill, governance, UI, standard, or current-state owner.

## Read Rule

Do not read every record. Start from the matching current owner, then select one
design by keyword only when prior decision context is necessary. Historical
design discovery starts at `docs/designs/legacy/README.md`.

## Active Records

| Record | Current role | Read when |
| --- | --- | --- |
| `2026-09-05-astra-agent-harness-migration-design.md` | Governing design for the repo-local Skill cutover, Engineering Workflow retirement, and final agent-routing topology. | Changing predictor_v3 agent instructions, repository-local Skills, governance routing, or reviewing the completed router retirement. |
| `2026-09-02-ahri-documentation-sync-plan.md` | Design Gate plan for synchronizing the AHRI Appendix M/M1 standard owners, Tkinter table adapter references, and recent Result Record traceability. | Implementing the documentation corrections identified in the 2026-09-02 AHRI documentation audit. |
| `2026-09-01-ahri-210-240-m-seer-hspf-audit-design-spec.md` | Active governing audit/design for adding Appendix M SEER/HSPF while preserving Appendix M1 SEER2/HSPF2 ownership and compatibility. | Implementing or reviewing AHRI 210/240 Appendix M calculator, M/M1 UI separation, formula/golden validation, or related owner boundaries. |
| `2026-07-14-train-admin-ui-ux-overhaul-document-set.md` | Navigation index for the Train/Admin overhaul, including the authoritative Phase 5 lifecycle design and the supporting Phase 5 UI/UX design. | Locating the correct Train/Admin phase design before implementation. |
| `2026-07-14-train-admin-ui-ux-overhaul-governing-design.md` | Governing product direction, owner boundaries, fixture/mock policy, mapping exchange contract, and delivery model for the Train/Admin overhaul. | Planning or reviewing any Train/Admin overhaul phase. |
| `2026-07-14-train-admin-phase-1-mapping-data-foundation.md` | Phase 1 design; repository-automated implementation, final audit, and merge complete. | Historical or boundary review for Train/Admin Phase 1. |
| `2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md` | Phase 2 design; implementation and merge complete, with deferred native evidence tracked separately. | Historical or boundary review for Data Mapping UX and exchange. |
| `2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md` | Phase 3 completed table-first Data Definition UX foundation; final audit and PR #16 merge history remain authoritative. | Historical acceptance or foundation review before Unified Feature Manager work. |
| `2026-07-17-train-admin-phase-4-unified-feature-manager.md` | Completed Phase 4 parent design for unified Predict/ML Feature authoring, safe multi-contract persistence, and live owner refresh. | Reviewing the complete Phase 4 goal, scope, slice boundaries, and final acceptance. |
| `2026-07-17-train-admin-phase-4a-current-state-contract-audit-closeout.md` | Approved Phase 4A amendment that closes the current-state audit and fixes canonical manifest, stable identity, ordering, generation, reconciliation, Target, and artifact boundaries before Slice 4B. | Starting or auditing Phase 4B and later Unified Feature Manager implementation. |
| `2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md` | Authoritative Phase 5 design for Train/Model UX, model lifecycle, analysis artifacts, shared CLI/campaign execution, and the bounded agent-assisted experiment loop. | Starting or auditing Phase 5B and every later Phase 5 implementation slice. |
| `2026-07-14-train-admin-phase-5-train-model-shell-ux-overhaul.md` | Supporting Phase 5 Train/Model and shell UI/UX direction. The authoritative lifecycle, CLI, campaign, agent-loop, migration, and implementation-order contract is the 2026-07-22 design. | Reviewing the detailed Train UI/UX flow alongside the authoritative Phase 5 design. |
| `2026-07-14-future-predict-ui-ux-overhaul-boundary.md` | Approved Layout B product direction, Result Review contract, existing-owner dependency map, missing Predict seams, implementation slices, and open compatibility gates. | Reviewing or preparing a material Predict input/result overhaul change. |
| `2026-07-13-all-standards-core-refactor-design.md` | Implemented governing inventory, contract, and private-owner design for active non-AHRI Calculator standard cores. | Refactoring or reviewing EN 14825, ISO 16358, KS C 9306, Brazil, or remaining active Calculator core routes. |
| `2026-07-12-ahri-seer2-hspf2-core-refactor-design.md` | Implemented governing design for the stable AHRI facades and private variable/legacy engines. | Reviewing or extending AHRI SEER2/HSPF2 core ownership, including future multi-capacity sibling engines. |
| `2026-07-12-calculator-table-architecture-design.md` | Implemented governing design for the three active Calculator table families. | Reviewing or changing Calculator table-family architecture. |
| `2026-07-11-calculator-ui-ux-unification-slice-0.md` | Active Calculator surface audit, target table policy, and migration Slice design. | Reviewing or implementing Calculator UI/UX unification. |
| `TEMPLATE_DESIGN_GATE.md` | Template for a new Design Gate record. | Creating a new design record. |
| `2026-07-10-agent-harness-report-lifecycle-redesign.md` | Current harness report/memory lifecycle redesign evidence. | Reviewing the conditional-record or Memory Review redesign. |
| `2026-06-27-pyside6-train-predict-rewrite-design-gate.md` | Governing Train/Predict PySide6 rewrite design gate. | Planning or reviewing the active Train/Predict architecture. |
| `2026-05-17-calculator-result-envelope-ml-adapter.md` | Unabsorbed calculator-result/ML-adapter boundary decision. | Implementing the future adapter or result-envelope boundary. |
| `2026-07-06-arc15-unified-data-definition-manager-foundation.md` | Historical Unified Data Definition owner/projection foundation extended by Phase 4. | Auditing schema/Feature ownership, projections, or Phase 4 persistence boundaries. |

## Legacy Records

Forty-five absorbed, deferred-resume, superseded, or completed records are
indexed under `docs/designs/legacy/README.md`. Their bodies preserve historical
paths and wording; use the legacy index and current physical path for discovery.

## Update Triggers

Update this index when:

- a new active design record is created at the root;
- an active record is absorbed by an owner or moved to legacy;
- a legacy record is explicitly re-promoted;
- an active record changes its current role.

Ordinary implementation or wording changes do not update this index.

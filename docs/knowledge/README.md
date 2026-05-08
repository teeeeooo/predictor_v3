# Knowledge Base

## Purpose

Knowledge documents are primarily consumed by coding agents.

This knowledge base is for ML feature engineering, physical sanity checks, data quality review, and result interpretation.

## Boundary

This knowledge base is not a source of truth for calculator logic.

It must not be used to modify calculator formulas, fixtures, region configs, or golden expected values. Standard calculator knowledge belongs in standard-specific dev_notes, official formulas, fixtures, and tests.

## Current Documents

- `physical_constraints_for_ml.md`: HVAC physical sanity checks, monotonicity caveats, ML constraint severity, and data review guidance.
- `hvac_ml_feature_engineering.md`: placeholder for HVAC ML feature groups, derived features, normalization ideas, and leakage risks.
- `hvac_ml_data_quality.md`: placeholder for HVAC ML data interpretation and review guidance.

## Maintenance Workflow

New content should usually come from grill-me style interviews with the user.

Capture raw context during the interview, then promote confirmed operational rules into concise guide sections. Keep source interview summaries short and move unresolved assumptions into open questions.

## Do / Do Not

Do:
- Keep documents short, operational, and useful for coding agents.
- Separate confirmed ML guidance from open questions.
- Mark equations as approximate sanity-check heuristics when they are used.

Do not:
- Use this folder as calculator authority.
- Copy long Q&A transcripts into guide documents.
- Add standard-specific formulas, golden references, or region config rules here.

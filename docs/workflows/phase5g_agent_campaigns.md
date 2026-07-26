# Phase 5G Agent-assisted Campaign Loop

`app_experiment.py` remains the machine-readable local entrypoint. Phase 5G
adds external-proposal orchestration; the application does not call an LLM or
invent hypotheses, parameters, Features, or follow-up experiments.

## Versioned contracts

- Campaign definition/record: `predictor_v3.agent_campaign.v1`
- Proposal: `predictor_v3.experiment_proposal.v1`
- Candidate gate: `predictor_v3.candidate_gate.v1`
- Leaderboard: `predictor_v3.campaign_leaderboard.v1`
- Recommendation: `predictor_v3.campaign_recommendation.v1`
- Budget extension: `predictor_v3.campaign_budget_extension.v1`

The Phase 5F `predictor_v3.experiment.v1` resolved specification remains the
training input. Accepted proposal deltas are resolved through that owner, and
the before specification, delta, after specification, hypothesis, expected
effect, and policy decision are durably written before training can start.

## Commands

```text
python3 -B app_experiment.py campaign-create DEFINITION.json [--campaign-id ID]
python3 -B app_experiment.py campaign-status CAMPAIGN_ID
python3 -B app_experiment.py campaign-budget CAMPAIGN_ID
python3 -B app_experiment.py campaign-proposal-submit CAMPAIGN_ID PROPOSAL.json
python3 -B app_experiment.py campaign-execute CAMPAIGN_ID PROPOSAL_ID
python3 -B app_experiment.py campaign-leaderboard CAMPAIGN_ID
python3 -B app_experiment.py campaign-incumbent CAMPAIGN_ID
python3 -B app_experiment.py campaign-recommendation-create CAMPAIGN_ID
python3 -B app_experiment.py campaign-recommendation CAMPAIGN_ID RECOMMENDATION_ID
python3 -B app_experiment.py campaign-complete CAMPAIGN_ID \
  [--without-recommendation]
python3 -B app_experiment.py campaign-budget-extend CAMPAIGN_ID NEW_TOTAL \
  --operator-reference APPROVAL_REFERENCE
python3 -B app_experiment.py campaign-pause CAMPAIGN_ID
python3 -B app_experiment.py campaign-cancel CAMPAIGN_ID
python3 -B app_experiment.py campaign-resume CAMPAIGN_ID
```

Proposal rejection is exit class `2` and contains a stable reason code. It
does not consume an iteration. Policy/budget, status, leaderboard, incumbent,
and recommendation reads use the same campaign store projected by Train UI.

## Budget and execution

The default total `max_iterations` is 5; campaign creation may configure a
bounded value from 1 through 100. Persisted consumed count and remaining
allowance survive process restart. Only the Phase 5F Core-owned structured
training-start acknowledgement consumes one iteration. Retry attempts retain
their existing total per-iteration allowance and do not consume another
iteration.

Agent campaign creation requires explicit primary and production-required
Target roles. Every declared guardrail Target must have a configured metric,
direction, and degradation threshold; the application does not invent missing
policy.

Proposal delta paths cannot address campaign budget. Once remaining allowance
is zero, proposal submission returns `campaign_budget_exhausted` and does not
start training; campaign exhaustion also writes an immutable recommendation
artifact while preserving the budget-exhausted campaign state. A separate
operator command records old total, new total,
consumed count, allowance before/after, and approval reference. Recommendation
may suggest an extension but never applies it.

## Proposal policy

One proposal normally declares one category:

- parameter/search-space adjustment;
- RFECV group override through the closed declarative registry projection;
- preprocessing contract change supported by the current shared resolver;
- existing Feature include/exclude;
- restricted shared-evaluator Derived experiment;
- target-scoped exploration.

A combined proposal must list at least two categories and records that causal
contribution is not separable. Unsupported preprocessing versions, unknown
RFECV groups, arbitrary fields/code/import/file/network/process requests,
execution-meaning changes, budget changes, and production mutations fail
before training.

## Gate, leaderboard, and baseline

Every completed iteration stores a versioned gate with production and
exploratory eligibility, reason codes, and evidence references. Production
recommendation is blocked by required-target failure, partial/incomplete
results, leakage or unreproducible Features reported by lifecycle evidence,
invalid Derived output, contract/integrity failure, configured guardrail or
instability violation, target-scoped exploration, or unpublished experimental
Features.

The leaderboard is rebuilt deterministically from persisted gates. It ranks
only gate-passing Candidates in this order: primary metric, guardrails,
stability, Feature count/complexity, reviewable physical/explainability
evidence, training cost/reproducibility, then lexical Candidate identity.
Missing qualitative evidence remains `review_required`; it is never converted
to an invented score. Campaign incumbent is separate from Active.

Baseline modes are `comparable_active`, `unbenchmarked_active`, and
`no_active`. Comparable Active requires matching current data hash and
evaluation evidence. Unbenchmarked Active remains Active without an
improvement claim. Bootstrap may select the first valid campaign Candidate as
incumbent but does not establish production readiness.

## Recommendation and authority

Recommendations are identity-bearing immutable history. They include
Candidate/runner-up/baseline, metric and stability evidence, Feature changes,
experimental Derived proposals, rejected Candidates and gate reasons,
limitations, next-action or extension suggestion, Phase 5H confirmation
requirement, and explicit approval-required state.

Recommendation generation never publishes a Definition, promotes or changes
Active, exports or replaces deployment, deletes artifacts, or claims final
production readiness. Final confirmation, locked final test, snapshot freeze,
migration, retention, and deletion remain Phase 5H.

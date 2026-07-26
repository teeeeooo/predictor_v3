# Phase 5F Headless Experiment Interface

`app_experiment.py` is the machine-readable entrypoint for the current
`predictor_v3.experiment.v1` contract. It uses JSON input and emits exactly one
`predictor_v3.experiment_output.v1` JSON object on stdout.

## Commands

```text
python3 -B app_experiment.py validate SPEC.json
python3 -B app_experiment.py resolve SPEC.json
python3 -B app_experiment.py run SPEC.json [--run-id ID]
python3 -B app_experiment.py run-status RUN_ID
python3 -B app_experiment.py run-result RUN_ID
python3 -B app_experiment.py run-logs RUN_ID
python3 -B app_experiment.py run-artifacts RUN_ID
python3 -B app_experiment.py campaign-start SPEC.json [--campaign-id ID]
python3 -B app_experiment.py campaign-status CAMPAIGN_ID
python3 -B app_experiment.py campaign-pause CAMPAIGN_ID
python3 -B app_experiment.py campaign-cancel CAMPAIGN_ID
python3 -B app_experiment.py campaign-resume CAMPAIGN_ID
python3 -B app_experiment.py lock-status
python3 -B app_experiment.py models
```

`validate` performs pure contract/default/safety validation. `resolve` reads an
existing current Definition generation and returns a structured validation
block when none exists. Service construction and both commands create no
generation, active-generation pointer, projection, lifecycle record, Candidate,
Active change, or writer-lock residue. A validated `run` or `campaign-start`
enters the mutation boundary and may invoke the existing Bootstrap initializer.
Status, result, lock, and model reads remain available while a writer owns
training.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | success or successful read/control request |
| `2` | invalid/unsupported specification or owned identity |
| `3` | workspace execution lock conflict |
| `4` | cancelled run/campaign |
| `5` | partial run |
| `6` | training failure or fail-closed blocked resume |
| `70` | internal interface failure |

The JSON `outcome` is the decision field. `message` is user guidance;
`diagnostics` is separate machine-readable internal detail. Natural-language
training logs are never the sole result signal.

## Specification boundary

The resolved contract contains experiment purpose, data request, target roles,
Feature policies, closed declarative experimental Derived definitions,
preprocessing, RFECV, Optuna, evaluation, campaign budget, reserved
early-stopping policy, bounded retry, and reserved recommendation thresholds.
Defaults resolve explicit experiment override, campaign configuration, then
project default.

Unknown fields and future versions fail closed. Experimental Derived supports
only the shared `safe_ratio` evaluator with known prior Feature operands,
constant zero-denominator policy, and a finite numeric fallback.

The contract has no executable-code, output-path, overwrite, promotion,
Definition publication, Active mutation, deletion, deployment replacement, or
budget-extension field. Phase 5G policy is preserved in records but does not
run an agent loop in Phase 5F.

## Campaign semantics

A Phase 5F campaign runs only the ordered objects in `campaign.experiments`.
`max_iterations` is a total cap and cannot be increased through this interface.

- Pause finishes the current run and stops before the next.
- Cancel terminates the current child process, publishes no incomplete
  Candidate, preserves safe terminal evidence, and remains resumable.
- Retry records another attempt identity for the same iteration and is bounded.
- Only the child job's structured Core-training-start acknowledgement consumes
  an iteration. Success, partial, failure, or cancellation after that event
  consumes it exactly once.
- Lock conflict consumes neither iteration nor attempt. Adapter/process-start
  failure preserves a non-started attempt and diagnostics, consumes no
  iteration, and remains explicitly resumable with the original budget.
- Resume reuses saved resolved contracts. Any specification,
  Definition/runtime, training, preprocessing, metric, or build identity
  mismatch returns a structured blocked state. Missing or uncertain saved or
  current build identity also blocks, never succeeds because two fallback
  strings compare equal, and does not rewrite existing campaign evidence.

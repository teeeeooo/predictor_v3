# Project Clean Architecture Boundary

## Purpose

This document is the codebase-wide owner for Clean Architecture / MVC boundary
rules in the active project.

It prevents responsibility mixing across:

- interface shells and views;
- domain engines and variant handlers;
- model training / inference paths;
- batch surfaces;
- file I/O and packaging scripts;
- spreadsheet automation, protected-file environments, and external system
  adapters;
- future GUI, web, or external interface shells.

This is not a single-screen, single-interface-framework, or single-domain
design note.

## Dependency Direction

Dependencies point inward:

```text
Shell / Adapter / View
-> Controller / Orchestrator / Application Service
-> Model / Domain
```

Model / Domain code must not depend on interface frameworks, file systems,
database/API clients, document automation, or platform-specific shell behavior.

External-system and interface-framework differences are absorbed at Shell /
Adapter / Infrastructure boundaries.

## Responsibility Definitions

### Model / Domain

Owns:

- calculation formulas;
- domain state;
- domain input validation;
- result data;
- pure domain variant / standard rules.

Does not own:

- interface framework behavior;
- file I/O;
- database/API calls;
- document automation or protected-file integration;
- application framework integration.

Model / Domain code should be testable without UI or external systems.

### Controller / Orchestrator / Application Service

Owns:

- workflow execution order;
- DTO / envelope conversion;
- Model calls;
- exception boundaries;
- orchestration between user action and Model.

Does not own:

- calculation formulas;
- domain decision rules;
- long widget-manipulation sequences;
- interface-framework-specific measurement or rendering policy.
- killable process lifecycle, stdout/stderr parsing, external tool execution,
  or artifact promotion/cleanup for long-running jobs.

Controller/service split is not sufficient if an application service directly
owns infrastructure execution that must vary by runtime. Long-running
execution, killable jobs, process lifecycle, stdout/stderr event parsing,
external tool execution, and artifact promotion/cleanup belong behind explicit
ports/protocols and outbound adapters.

Examples:

- Train production execution: `TrainingExecutionPort` -> process runner adapter
  such as `QProcessTrainingRunner`.
- Predict execution: `PredictionExecutionPort` -> PySide/QThread runner or
  another runtime runner.
- Predict result attachment: the Qt-free application/session boundary pins one
  immutable execution context and runtime-owned expected-target projection per
  case request. It accepts an executed result only when session, case, run,
  case-input revision, runtime semantics, loaded model identity, target
  identities/metadata, and aggregate status all match. Cancellation and
  infrastructure failure carry the same context through this gate. User-facing
  progress and summaries count canonical accepted dispositions, not worker
  transport progress. Direct single/bulk session setters accept only
  non-executed `pending`, `running`, and `invalid` state; every
  `complete`/`partial`/`error`/`cancelled` row uses canonical acceptance
  regardless of payload shape. A worker or Qt view never owns reconciliation.
- Calculator execution: `CalculatorUseCase` -> core calculator dispatcher
  adapter, not direct orchestration inside UI sections.

### Shell / Adapter / Infrastructure

Owns:

- GUI / web / external interface binding;
- spreadsheet automation, protected-file environment, file system, database,
  network API, or external document integration;
- external format import/export;
- interface-specific measurement;
- platform-specific error handling.

These concerns should be isolated behind interfaces, protocols, adapters, or
explicit shell owners when they are reused or likely to repeat.

### View / Presentation

Owns:

- widget construction;
- screen display;
- user input collection;
- user event forwarding.

Does not own:

- complex calculation;
- file I/O;
- schema policy;
- measurement policy;
- geometry / refit orchestration;
- repeated mapping / routing / formatting rules.

### Policy / Contract Owner

Owns repeated rules such as:

- schema / public API / result envelope contracts;
- UI/UX contract;
- table contract;
- window geometry / viewport policy;
- domain variant / region / standard rules;
- import/export shape rules.

If a rule can repeat across screens, domain variants, standards, or interface
frameworks, it should move out of a local View/helper and into an owner
document, adapter, service, or contract module.

## Boundary Smells / Stop Conditions

Stop implementation and decide the owner boundary first when any of these
appear:

- one class/file owns View + Controller + Adapter + Policy at the same time;
- a View performs calculation orchestration, file I/O, schema conversion, or
  measurement policy directly;
- a Model imports interface framework, file path loading, document automation,
  database/API, or application framework concerns;
- a Controller contains calculation formulas or domain decision rules;
- interface-specific Shell / Adapter logic leaks into core/domain;
- the same measurement, mapping, formatting, or routing rule appears in
  multiple screens;
- a local hotfix is likely to repeat for another domain variant, standard,
  interface framework, or shell;
- result reports repeatedly show the same smoke bug class.

When a stop condition appears, create a small owner-boundary preflight or
report slice before implementation unless the user explicitly approves a scoped
hotfix.

Structure guard warnings are not architectural acceptance. When a new or
substantially changed source file exceeds a soft LOC limit, the report should
either explain why the current responsibilities can stay together for this slice
or set the next action to a responsibility split audit. If repeated mapping,
formatting, routing, result formatting, or lifecycle handling accumulates in a
View or Adapter, revisit the owner boundary before adding more responsibility.

## Observed Example / Evidence

Example names are evidence, not scope boundaries. A concrete dynamic GUI
surface sizing issue was observed in a calculator screen, but the policy above
is the source of truth.

The problem grew because one View accumulated widget composition, hidden-tab
measurement, refit scheduling, geometry application, scroll cleanup, and
domain-variant trigger handling. Splitting the responsibilities clarified the
boundary:

- shell/template owns reusable content-hugging form behavior;
- scheduler owns event-loop refit orchestration;
- geometry primitive helper owns parse/format/cap/clamp math;
- measurement adapter/provider owns visible-content measurement;
- View consumes those owners and forwards triggers.

Concrete examples from the current history include Tkinter, Hong Kong profile
switching, and content-hugging window behavior. Those names remain examples
only; the same lesson applies to future GUI, web, batch, and model-operation
surfaces.

## How To Apply

Before implementation, run a short boundary triage:

- Which layer owns the new responsibility: Model, Controller, Shell/Adapter,
  View, or Policy?
- Does the change make one class/file own multiple responsibilities?
- Is the rule likely to repeat across domain variants, standards, screens, or
  interface frameworks?
- Can this be tested without UI or external systems?

Small behavior-preserving hotfixes do not require a large preflight when they
add no new responsibility. If repeated smoke failures show the same bug class,
promote the issue to owner-boundary work before adding another local patch.

## Source File Owner Boundary Policy

To prevent scattering files and building architectural debt, we enforce a codebase-wide policy for organizing new files:

1. **Determine the Owner Boundary First**: Before creating any new source file, decide which feature, domain, standard, or tool owns the functionality.
2. **Avoid Flat Files in Broad Folders**: Do not add feature-specific flat files directly into broad, root-level directories (e.g., `apps/calculator/ui/`, `core/`, `tests/`, `tools/`). Broad folders are not dumping grounds.
3. **Establish a Feature Package First**: If a feature is expected to expand to multiple responsibilities (e.g., having its own data models, adapters, table models, views, controllers, or helper files), define a feature package (a subdirectory with `__init__.py`) instead of scattering individual files.
4. **Halt on Out-of-Scope Packages**: If creating a package is outside your current task scope, do not place temporary flat files in broad folders. Stop and report for clarification.
5. **Clean SoC via Package Isolation**: Separation of concerns (SoC) or MVC should be achieved by dividing responsibilities *within* the feature package directory, not by spreading flat files across different broad directories.
6. **No New Flat Debt**: Existing legacy flat structures are preserved until they are audited and refactored under a separate task, but adding new flat debt is strictly prohibited.

### Visual Examples

* **Good (Clean Package Boundaries)**:
  * `apps/calculator/ui/en14825/seer_models.py`
  * `apps/calculator/ui/en14825/seer_adapter.py`
  * `apps/calculator/ui/en14825/seer_table_model.py`
  * `apps/calculator/ui/batch/models.py`
  * `apps/calculator/ui/batch/controller.py`

* **Bad (Flat File Dumping)**:
  * `apps/calculator/ui/en14825_seer_models.py`
  * `apps/calculator/ui/en14825_seer_adapter.py`
  * `apps/calculator/ui/sections/en14825_seer_adapter.py`
  * `apps/calculator/ui/sections/en14825_seer_table_model.py`
  * `core/en14825_helper_extra.py`
  * `core/new_standard_misc.py`
  * `tests/test_newstandard_everything.py`

## Reference Parity / Standardization Gate


Before creating a new UI surface, script, helper, adapter, workflow path, or
reusable component, check whether an existing stable implementation or workflow
already covers the same concerns.

The goal is not forced reuse; it is to avoid repeatedly rediscovering already
solved behavior bugs, lifecycle handling, error handling, validation flow,
import/export shape, cleanup/dispose, idempotency, and report workflow patterns.

- If the existing reference fits, prefer reuse or adaptation.
- If it does not fit, record why it was not reused.
- If the new implementation diverges in user-visible behavior, lifecycle
guarantees, or ownership boundaries, leave parity evidence in the result report.
- If unresolved parity gaps remain, record them as known risks or next actions.

This gate applies to every layer (Model, Controller, Shell, View, Policy), not
only to UI surfaces.

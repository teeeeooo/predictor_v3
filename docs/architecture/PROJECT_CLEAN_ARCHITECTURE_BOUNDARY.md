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

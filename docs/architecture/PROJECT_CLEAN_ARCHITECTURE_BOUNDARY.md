# Project Clean Architecture Boundary

## Purpose

This document is the project-wide owner for Clean Architecture / MVC boundary
rules in `predictor_v3`.

It prevents responsibility mixing across:

- UI shells and views;
- calculator engines and profile handlers;
- ML train/predict paths;
- batch surfaces;
- file I/O and packaging scripts;
- Excel / DRM / external system adapters;
- future Web, PySide/PyQt, WPF, or other shells.

This is not a Tkinter-only rule and not a calculator-screen design note.

## Dependency Direction

Dependencies point inward:

```text
Shell / Adapter / View
-> Controller / Orchestrator / Application Service
-> Model / Domain
```

Model / Domain code must not depend on UI toolkits, file systems, DB/API
clients, Excel, web frameworks, or platform-specific shell behavior.

External-system and toolkit differences are absorbed at Shell / Adapter /
Infrastructure boundaries.

## Responsibility Definitions

### Model / Domain

Owns:

- calculation formulas;
- domain state;
- domain input validation;
- result data;
- pure profile / region / standard rules.

Does not own:

- UI toolkit behavior;
- file I/O;
- DB/API calls;
- Excel or DRM integration;
- web framework integration.

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
- toolkit-specific measurement or rendering policy.

### Shell / Adapter / Infrastructure

Owns:

- Tkinter / PySide / WPF / Web binding;
- Excel / xlwings / DRM / file system / DB / API integration;
- external format import/export;
- toolkit-specific measurement;
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
- calculator profile / region rules;
- import/export shape rules.

If a rule can repeat across screens, profiles, standards, or toolkits, it should
move out of a local View/helper and into an owner document, adapter, service, or
contract module.

## Boundary Smells / Stop Conditions

Stop implementation and decide the owner boundary first when any of these
appear:

- one class/file owns View + Controller + Adapter + Policy at the same time;
- a View performs calculation orchestration, file I/O, schema conversion, or
  measurement policy directly;
- a Model imports UI toolkit, file path loading, Excel, DB/API, or web framework
  concerns;
- a Controller contains calculation formulas or domain decision rules;
- toolkit-specific Shell / Adapter logic leaks into core/domain;
- the same measurement, mapping, formatting, or routing rule appears in
  multiple screens;
- a local hotfix is likely to repeat for another profile, standard, toolkit, or
  shell;
- result reports repeatedly show the same smoke bug class.

When a stop condition appears, create a small owner-boundary preflight or
report slice before implementation unless the user explicitly approves a scoped
hotfix.

## Window Sizing Lesson

The Tkinter/Hong Kong lower blank space and flicker issue is an example, not
the source of truth.

The problem grew because one View accumulated widget composition, hidden-tab
measurement, refit scheduling, geometry application, scroll cleanup, and
profile-specific trigger handling. Splitting the responsibilities clarified the
boundary:

- shell/template owns reusable content-hugging form behavior;
- scheduler owns event-loop refit orchestration;
- geometry primitive helper owns parse/format/cap/clamp math;
- measurement adapter/provider owns visible-content measurement;
- View consumes those owners and forwards triggers.

The same lesson applies to future PySide, WPF, Web, batch, and ML UI surfaces.

## How To Apply

Before implementation, run a short boundary triage:

- Which layer owns the new responsibility: Model, Controller, Shell/Adapter,
  View, or Policy?
- Does the change make one class/file own multiple responsibilities?
- Is the rule likely to repeat across profiles, standards, screens, or
  toolkits?
- Can this be tested without UI or external systems?

Small behavior-preserving hotfixes do not require a large preflight when they
add no new responsibility. If repeated smoke failures show the same bug class,
promote the issue to owner-boundary work before adding another local patch.

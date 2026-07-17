# Future Predict UI/UX Overhaul — Boundary

Status: deferred design boundary  
Date: 2026-07-14  
Prerequisite: Train/Admin Phases 1–5 complete

## 1. Purpose

Record the intended continuation after the Train/Admin overhaul without designing
Predict prematurely.

Predict remains the next major UI/UX target. Detailed design begins only after the
Train/Admin common components, table behavior, status model, and
definition/mapping workflows are stable.

## 2. Preserved Current Direction

The future overhaul preserves unless a later audit explicitly changes them:

- one visible row represents one prediction case;
- input, mapping/auto, calculated, prediction result, and status fields coexist in
  the unified case-table workflow;
- schema-driven column ownership;
- existing prediction controller/application/service boundaries;
- existing mapping dropdown/autofill and cascade behavior;
- feature name/order/type compatibility;
- model registry and artifact compatibility;
- non-blocking prediction execution;
- spreadsheet table UX requirements.

## 3. Prerequisites

Before detailed Predict design:

- Train/Admin shared PySide6 components are stable;
- Data Definition can safely express supported column and mapping changes;
- Data Mapping can manage dynamic attributes and exchange data;
- shell-level model/mapping/restart state is established;
- populated fixture/mock prediction workflows exist;
- the current Predict UI receives a fresh audit using populated, warning, error,
  and batch states.

## 4. Expected Future Audit Areas

- unified case-table density and grouped headers;
- batch row creation, duplication, deletion, copy/paste, and navigation;
- distinction between manual, mapping-backed, calculated, prediction-result, and
  status cells;
- mapping cascade discoverability;
- validation and warning placement;
- prediction progress and cancellation;
- per-row versus global issues;
- result interpretation and comparison;
- empty/missing model/missing mapping states;
- table width, frozen identity columns, scrolling, and responsive layout;
- reuse of Train/Admin status, issue, toolbar, dialog, and table components.

## 5. Boundary with Current Program

Train/Admin Phases 1–5 may:

- create reusable components intended for Predict;
- correct shared component defects;
- keep embedded Predict status synchronized at shell level.

They must not:

- restructure Predict's internal workspace;
- change case-table public behavior;
- alter prediction formulas or model-input adapters;
- perform a hidden partial Predict redesign inside a Train/Admin slice.

## 6. Detailed Design Trigger

Create the detailed Predict design only after Phase 5 closeout confirms:

- shared component inventory;
- current Predict adoption gaps;
- stable schema/mapping/model readiness flows;
- representative fixture/mock prediction states;
- no unresolved Train/Admin owner ambiguity.

## 7. Non-goals

- Defining exact Predict screens now.
- Choosing pixel-level layout before a fresh audit.
- Changing prediction runtime or ML contracts in this boundary record.

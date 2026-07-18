# Design Gate Summary

## Goal

Phase 4C+4D Unified Feature Manager 위에 identity 기반 Derived authoring,
deterministic dependency DAG, shared evaluator, prepared Preview/Apply, generation
Save 경계를 추가한다. 기존 8개 `safe_ratio` 계산값과 순서를 유지하고 Train과
Predict가 같은 계산 owner를 사용하게 한다.

## Confirmed Decisions

- canonical Derived operand는 Feature 또는 Derived stable identity를 참조한다.
- authoring operation은 `safe_ratio` 하나만 지원한다.
- zero-denominator policy는 `constant` 하나이며 `zero_value`는 finite numeric
  constant다. boolean, NaN, positive/negative infinity는 거부하고 빈 값은
  `0.0`으로 정규화한다.
- 기존 8개 Derived의 `zero_value`는 `0.0`으로 유지한다.
- 새 Derived는 inactive로 생성하며 active ML projection을 암묵적으로 바꾸지
  않는다.
- 활성 Derived의 의미 또는 activation 변경은 Preview까지 허용하되 기존
  retraining/migration Save guard를 통과하지 못하면 publication을 차단한다.
- execution order는 dependency DAG에서 계산하며 기존 canonical order를
  deterministic tie-break로 사용한다. Derived Move command는 제공하지 않는다.
- legacy name-based generation은 versioned decode로 읽고, 정확히 하나의 source
  identity로 해석되지 않으면 actionable validation failure로 거부한다.
- 새 publication은 identity-based contract version을 사용한다.
- representation-only migration은 Derived runtime semantics와 model compatibility
  fingerprint를 바꾸지 않는다.

## Core vs Handler Boundary

- Canonical contract: Derived identity, identity operand, operation, policy/value,
  active state.
- Domain/core: immutable commands, graph validation, downstream evidence,
  deterministic topological ordering.
- Shared evaluator: `safe_ratio` 계산 의미와 current missing/non-numeric/NaN/
  infinity semantics.
- ML adapter: current DataFrame shape와 immutable canonical snapshot을 evaluator에
  전달하는 compatibility facade.
- Application/controller: prepared command, stale protection, selection, dirty state,
  Preview, Save orchestration.
- View: candidate 선택과 intent 수집, evidence 표시만 수행한다.
- Repository: immutable generation publication과 historical version read/rollback.

## Data Shape / API Boundary

- v2 Derived DTO는 numerator/denominator identity와 explicit constant policy/value를
  저장한다.
- v1 decode는 name operand를 Feature/Derived identity로 deterministic resolution한
  normalized snapshot을 제공한다. v1 bundle byte/fingerprint verification은 계속
  가능해야 한다.
- evaluator는 repository/filesystem/UI/global mutable state를 읽지 않고 immutable
  definition snapshot과 명시적 DataFrame을 받는다.
- 기존 `core.ml.preprocessing.calculate_derived_features()` import path는 thin
  compatibility facade로 유지한다.

## Required Tests

- 기존 production evaluator 대비 normal/negative/zero/floating/NaN/missing/
  non-numeric/infinity/dtype/order/input-copy golden parity.
- Feature-to-Derived 및 Derived-to-Derived DAG, deterministic order, self/direct/
  indirect cycle, missing/inactive/type/downstream guards.
- Rename identity 유지, Add/Duplicate 새 identity, Feature ML rename operand 유지,
  legacy deterministic migration과 ambiguous/missing rejection, rollback read,
  representation-only fingerprint parity.
- command atomicity, prepared Preview/Apply parity, stale rejection, inactive Save,
  model-impacting blocker, dependency/formula evidence.
- Train/Predict evaluator parity, leakage/mandatory/Target/current model order regression.
- publication failure/stale parent/history immutability와 structure/change gates.

## Migration / Refactor Path

1. legacy production behavior를 golden test로 잠근다.
2. v2 contract와 legacy compatibility decode/encode verification을 추가한다.
3. graph validator와 shared evaluator를 canonical core owner로 추가한다.
4. Derived draft/commands/candidate/fingerprint/save 경계를 연결한다.
5. Train/Predict preprocessing을 compatibility facade를 통해 shared evaluator로
   전환하고 하드코딩 formula를 제거한다.
6. Unified Feature Manager에 restricted Derived dialogs/actions/Preview evidence를
   연결한다.
7. focused regression, repository, structure/change gate를 수행한다.

## Risks

- historical v1 bundle은 당시 projection bytes와 fingerprint metadata를 그대로
  검증해야 하므로 compatibility normalization과 publication encoding을 분리해야
  한다.
- inactive canonical semantics fingerprint와 active model compatibility fingerprint를
  분리하지 않으면 safe inactive authoring이 잘못 차단될 수 있다.
- current runtime generation cutover는 Phase 4H 범위이므로 이번 adapter는 현재
  composition에서 명시적 immutable snapshot만 공급한다.
- Windows native UI smoke는 이 환경에서 통과로 주장하지 않는다.

## Non-goals

Phase 4F/4G/4H, arbitrary formula language, 새 operation, 자동 training/retraining,
promotion/activation, Predict UX 개편, mapping/model artifact 변경, Windows packaging.

## Next Codex Implementation Prompt

이 문서의 경계대로 Phase 4E를 구현하고 golden/DAG/identity/migration/command/UI/
runtime/persistence regression 및 structure/change gate를 통과시킨다.

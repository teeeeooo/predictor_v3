# PROJECT CHARTER

## 1. 프로젝트 목적 및 최종 목표
`predictor_v3`는 단순 계산기가 아니라, **시험 데이터 → 규격 계산 → ML 예측 → 목표 성능/효율 역방향 탐색**으로 이어지는 통합 엔지니어링 도구입니다.
최종 목표는 목표 CSPF, HSPF, SEER, SCOP 또는 목표 성능을 만족하기 위한 capacity, power, part-load 조건을 역방향으로 탐색하는 엔진을 구축하는 것입니다.
장기적으로 사용자가 목표 성능과 대상 지역/규격을 입력하면 후보 HW 조합을 평가하고 추천하는 역탐색 엔진을 구축합니다.
계산기는 이 과정에서 지역/규격별 CSPF/HSPF/SEER2/HSPF2/SCOP 등을 산출하는 계절효율 평가 엔진 역할을 합니다.

## 2. 진행 순서 원칙
작업은 다음 순서로 진행하여 시스템의 안정성을 확보합니다.
1. 계산식 신뢰성 확보
2. Golden/Smoke/Validation 테스트 구축
3. 입력 구조 안정화
4. UI 연결
5. Predictor 연동
6. 역방향 탐색(Backward Search) 엔진 구현

## 3. 핵심 아키텍처 원칙
- **공통 엔진 우선:** 지역별(Region) 하드코딩을 먼저 적용하지 않고, 공통 엔진 / profile / config / handler 구조를 먼저 검토하여 확장성을 유지합니다.
- **UI 툴킷 정책 (UI Toolkit Policy):**
  - Calculator UI는 Tkinter 전환을 활성 마이그레이션 방향(active migration direction)으로 진행합니다.
  - Train/Predict의 신규 재작성(rewrite)은 PyQt5 migration이 아니라 PySide6 기준 신규 작성으로 진행합니다.
  - 기존 `ui/` PyQt5 Train/Predict 경로는 당장 삭제하지 않고 reference-only / legacy path로 유지합니다.
  - PyQt6로의 전환은 계속 금지합니다.
- **API 안정성:** `core` 모듈의 calculator public API는 신중하게 유지합니다.
- **UI 분리 및 경계 (UI Separation & Boundary):**
  - Calculator, Train, Predict 애플리케이션의 화면 및 비즈니스 로직 책임을 명확히 구분하며, 작업을 서로 섞지 않습니다.
  - 장기적인 애플리케이션 패키지 경계는 `apps/{calculator,train,predict}/` 구조를 지향합니다.
- **Schema boundary 분리:** region config, HW candidate input, ML output/result schema, calculator result schema를 섞지 않습니다.
- **Architecture contract 위치:** calculator profile resolver와 역탐색 boundary의 상세 기준은 `docs/architecture/project_architecture.md`에 둡니다.

## 4. 장기 마일스톤

### Phase 1 — 계산 엔진 안정화
- ISO 16358, KS C 9306, EN14825, AHRI 210/240 계산 경로를 golden/smoke/validation test로 보호한다.
- 지역 차이는 가능한 한 `data/region_configs/`와 profile/config/handler 구조로 표현한다.

완료 기준:
- 주요 계산 경로가 regression test로 보호된다.
- 계산 로직 변경 시 전체 테스트로 회귀를 방어할 수 있다.

### Phase 2 — Calculator UI v1 (Tkinter Migration)
- 엔지니어가 규격 계산 입력값을 직접 넣고 결과를 확인할 수 있는 Tkinter 기반 UI를 구축하고 마이그레이션한다.
- 우선 ISO16358/CSPF부터 안정화하고, HSPF/EN14825/AHRI는 단계적으로 연결한다.

완료 기준:
- UI 입력값이 core calculator와 정확히 연결된다.
- 계산 결과와 주요 중간값을 확인할 수 있다.
- Train/Predict UI를 깨지 않는다.

### Phase 3 — Predictor 파이프라인 안정화
- PySide6 기준 Train/Predict UI shell을 `apps/predict/`, `apps/train/` 아래에서 새로 작성하고, `app_predict.py` / `app_train.py`는 thin entrypoint로 유지한다.
- feature mapping, target별 leakage 방지, model output 신뢰성을 확보한다.

완료 기준:
- 학습/예측 결과가 재현 가능하다.
- 주요 데이터 변환 과정이 문서화된다.

### Phase 4 — Calculator ↔ Predictor 연동
- 예측된 capacity/power/성능값을 규격 계산기에 연결한다.
- predictor output이 calculator input으로 안전하게 변환되도록 한다.

완료 기준:
- 단위, 조건점, region profile 불일치를 방어한다.
- 예측 결과 기반 CSPF/HSPF/SEER/SCOP 계산이 가능하다.

### Phase 5 — 역방향 탐색 엔진
- 목표 효율 또는 목표 성능을 만족하기 위한 입력 조합을 역방향으로 탐색한다.
- 예: 목표 CSPF 달성을 위한 capacity/power/part-load 조건 추천.

완료 기준:
- 사용자가 목표값을 입력하면 가능한 조합 또는 개선 방향을 제안한다.
- 규격 계산 제약과 ML 예측 제약을 함께 고려한다.

## 5. 문서 운영 원칙

- 규칙은 `AGENTS.md`에 둔다.
- 상세 작업 라우팅은 `AGENT_TASK_ROUTER.md`에 둔다.
- 장기 방향과 Phase 1~5는 `PROJECT_CHARTER.md`에 둔다.
- Phase / Arc / Milestone 지도는 `project_brief.md`에 둔다.
- 현재 slice, 다음 action, blocker, active constraints, hold 상태는 `docs/WORK_PLAN.md`에 둔다.
- 명시적으로 요청된 다음 세션 handoff pointer는 `docs/WORK_PLAN.md`의 `Session Handoff`에 둔다.
- 작업 기록과 try/fail/success, milestone decision과 lesson은 `project_log.md`에 둔다.
- 리팩토링 후보와 구조 분리 기준은 `docs/REFACTOR_PLAN.md`에 둔다.
- 같은 내용을 여러 문서에 중복으로 길게 기록하지 않는다.

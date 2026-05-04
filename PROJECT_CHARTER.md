# PROJECT CHARTER

## 1. 프로젝트 목적 및 최종 목표
`predictor_v3`는 단순 계산기가 아니라, **시험 데이터 → 규격 계산 → ML 예측 → 목표 성능/효율 역방향 탐색**으로 이어지는 통합 엔지니어링 도구입니다.
최종 목표는 목표 CSPF, HSPF, SEER, SCOP 또는 목표 성능을 만족하기 위한 capacity, power, part-load 조건을 역방향으로 탐색하는 엔진을 구축하는 것입니다.

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
- **PyQt5 유지:** PyQt5를 표준으로 유지하며, PyQt6로의 전환은 금지합니다.
- **API 안정성:** `core` 모듈의 calculator public API는 신중하게 유지합니다.
- **UI 분리:** Train/Predict UI 작업과 계산기 UI 작업을 섞어 진행하여 기존 코드를 깨뜨리지 않도록 철저히 분리합니다.

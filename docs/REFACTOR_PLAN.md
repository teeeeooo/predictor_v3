
## 0. 문서 목적

이 문서는 `predictor_v3` 프로젝트의 리팩토링 후보를 한 곳에서 관리하기 위한 백로그다.

리팩토링은 기능 구현보다 앞서서 진행하지 않는다. 이미 검증된 계산 엔진을 성급하게 분리하거나 구조를 크게 바꾸지 않고, 실제로 반복되는 문제와 확장 병목이 확인된 항목부터 단계적으로 처리한다.


[REFACTOR_PLAN.md 업데이트 원칙]:
- 새 TODO를 추가할 때는 같은 섹션의 완료/구식 TODO를 반드시 같이 정리한다.
- 완료 상세는 project_log.md로 보내고, REFACTOR_PLAN.md에는 현재 남은 작업만 남긴다.
- “완료됨” 리스트를 누적하지 않는다.
- `완료`, `구현 완료`, `검증 완료` 표현이 늘어나면 해당 섹션을 축약 후보로 본다.

---

## 1. 현재 프로젝트 상태 요약

| 영역 | 현재 상태 | 리팩토링 판단 |
|---|---|---|
| ISO 16358 CSPF | KS, ISO T1, ISEER, Hong Kong, SASO T3 검증 완료. | Phase 1 UI 노출 완료. cspf_profile/schema 전환은 HSPF 공통화 이후 수행. |
| ISO 16358 HSPF | KS C 9306 profile 및 검증 체계 구축 완료. | ISO16358-2 HSPF 공통화가 차기 핵심 과제. |
| AHRI 210/240 | SEER2/HSPF2 Variable-capacity 구현 완료. | Phase 1 UI 연결 대기. |
| EN 14825 | SEER/SCOP 주요 계산 및 검증 완료. | 중복 코드 확인 후 리팩토링 여부 검토 필요 |
| Region config | Production/Planned config 분리 관리 중. | 규격 근거 없는 임의 수정 금지. |
| Docs | 4대 문서 구조(notes/dev/design/glossary)로 정리 중. | 2차 리팩토링 마무리 단계. |
| UI calculator | Calculator UI v1 기본 연결 진행 중. | SASO T3 노출 완료. Multi 입력 등은 후속 작업. |
| ML pipeline | Trainer/Predictor pipeline 재개 대기. | 학습 데이터 환경 확보 후 진행. |

---

## 2. 전체 우선순위

| 우선순위 | 항목 | 상태 | 판단 |
|---|---|---|---|
| P0 | 계산 결과 회귀 방어 | 진행 중 | golden / smoke / validation test 유지 |
| P1 | 문서 리팩토링 2차 마무리 | 진행 중 | notes/dev/design/glossary 체계 확정 |
| P1 | ISO 16358-2 HSPF 공통화 | 예정 | 한국 외 HSPF 확장 및 엔진 통합 |
| P2 | CSPF/HSPF profile schema 전환 | 예정 | Predictor 연동 전 필수 안정화 단계 |
| P2 | Calculator UI v1 마무리 | 진행 중 | 상세 결과 graph/table 개선 |
| P3 | Predictor / Calculator 연동 | 예정 | ML 예측값 기반 seasonal metric 자동 산출 |
| P4 | 역방향 탐색 엔진 (MVP) | 예정 | 목표 성능 기반 HW 조합 추천 |

---

## 3. 실행 원칙

### 3.1 지금 지켜야 할 원칙

- 한 번에 대규모 구조 변경을 하지 않는다.
- 계산 결과가 검증된 엔진은 region config 확장 전까지 보존한다.
- golden expected를 임의로 수정하지 않는다.
- region config는 규격 또는 공식 계산시트 근거가 있을 때만 수정한다.
- 코드 리팩토링보다 validation test 추가를 우선한다.
- UI와 ML pipeline은 계산 엔진 안정화 이후 연결한다.

### 3.2 Codex / coding agent 작업 원칙

- `AGENTS.md`의 Lite 규칙만 기본으로 읽는다.
- 코드 수정 전 변경 범위를 먼저 제한한다.
- 계산식 변경 시 반드시 regression/golden 결과를 함께 보고한다.
- 문서만 수정하는 작업에서는 코드, test, JSON을 수정하지 않는다.

---

## 4. ISO 16358 리팩토링 계획

### 4.1 현재 상태

`ISO16358Calculator`는 현재 ISO/KS CSPF/HSPF의 모든 경로를 포함하고 있다. 클래스가 비대해지고 있으나 테스트 결과가 안정적이므로 당분간 구조를 유지한다.

### 4.2 지금 하지 않을 작업

- `ISO16358Calculator` 클래스/파일 강제 분리
- region별 subclass/inheritance 구조 도입
- plugin architecture 도입
- generic ISO HSPF의 무리한 규격 확장

### 4.3 나중에 검토할 분리 후보

| 후보 모듈 | 역할 |
|---|---|
| `calculator_iso16358.py` | common entry point, CSPF path, generic HSPF fallback |
| `regions/ks_c9306.py` | KS C 9306 전용 helper 분리 |
| `region_config_schema.py` | schema validation 전담 |

### 4.4 분리 검토 트리거

- 클래스 크기가 1800줄을 초과할 때
- KS 외 region-specific 계산 예외가 추가될 때
- 공통 path 수정 시 기존 테스트가 반복적으로 깨질 때

---

## 5. ISO 16358 CSPF Region Config 확장 계획

### 5.1 목표

엔진 수정 없이 config와 test profile만으로 국가별 규격을 확장한다.

### 5.2 현재 상태

- **완료**: `cspf_test_profile` 도입, SASO T3 golden regression 완료.
- **기록**: 세부 테스트 로그는 `project_log.md` 및 `docs/iso16358/` 참조.

### 5.3 Phase R3 — Schema 마이그레이션 (Predictor 연동 전 필수)

- **목표**: 기존 region config를 `cspf_test_profile` 기반 schema로 완전 전환.
- **방향**: HSPF 역시 동일한 profile/config 구조로 통합.
- **보호**: 기존 public API 및 regression 결과(Korea 6.504 등) 유지.

### 5.4 계산기 Phase 1 배포 범위 & UI v1 원칙

- **포함**: Korea, ISO T1 default, India, Hong Kong, EN14825, AHRI
- **UI 원칙**: 검증된 profile만 노출하며, 미검증 optional matrix는 비활성화.

### 5.5 ISO 16358 CSPF xlsm 구조 확인 요약
- **결론**: T3는 T1과 같은 bin-row template에 piecewise anchor를 적용하는 구조이므로 generic `cspf_profile` schema가 적합하다.
- **남은 작업**: T1/T3 segment, point source matrix, optional input policy를 schema로 안정화한다.
- **상세 근거**: cell range 및 분석 기록은 `project_log.md` 및 `docs/iso16358/` 참조.

---

## 6. KS C 9306 유지보수 계획

### 6.1 현재 확정된 방향

한국 고유 관행(시험점, 보정계수)을 존중하여 common ISO와 무리하게 통합하지 않는다.

- KS HSPF는 `ks_c_9306_hspf` 전용 프로필 사용.
- HSPF load line은 한국 공식 시트 기준(`rated_cap * 0.82`) 유지.
- 규격과 시트 간 차이는 문서로 보존.

### 6.2 주의 항목

- AS/NZS 3823.4.2 규격 확인 전 호주/뉴질랜드 구현 금지.
- 2°C 외삽 시 선형보간 방식(`-7 ↔ 7`) 유지.

---

## 7. AHRI 210/240 리팩토링 계획

### 7.1 현재 상태

SEER2/HSPF2 v3 full variable-capacity path 구현 및 검증 완료.

### 7.2 지금 할 일

- 대규모 리팩토링 지양, 문서 및 테스트 유지.
- 신규 case 발견 시 golden test 추가.

### 7.3 Config cleanup mini phase

- 단기 TODO: `data/usa_hspf2.json`을 `data/region_configs/usa_hspf2.json`으로 이동하고 테스트/문서 참조를 갱신한다.
- 보류: `data/region_configs/usa.json`과 HSPF2 config의 완전 통합은 현재 flat schema 충돌 위험 때문에 보류한다.
- 재검토 조건: `cooling` / `heating` namespace 또는 loader compatibility 설계 후 재검토한다.

### 7.4 보류 항목

- SEER2/HSPF2 config 완전 통합은 namespace schema migration 또는 loader compatibility가 준비될 때까지 보류한다.

---

## 8. EN 14825 리팩토링 계획

### 8.1 현재 상태

SEER/SCOP 엔진 구현 완료. 특이사항은 문서로 관리.

### 8.2 보류 항목

- ISO 16358과 공통 seasonal engine 통합 (과설계 위험).

---

## 9. Docs 리팩토링 계획

### 9.1 현재 목표 구조

```text
docs/
├── ahri210240/     (glossary, notes, design_notes, dev_notes)
├── en14825/        (en14825_glossary, en14825_notes, en14825_design_notes, en14825_dev_notes)
└── iso16358/       (glossary, notes, design_notes, dev_notes, regions/ks_c_9306/...)
```

### 9.2 문서 역할 구분

- **glossary**: 용어/약어
- **notes**: 규격/계산 구조
- **design_notes**: 설계 관점/전략
- **dev_notes**: 구현 주의사항/테스트 전략

### 9.3 현재 문서 정리 상태

- **정리 방향**: notes(계산)/dev_notes(작업)/design_notes(설계)/glossary(용어) 구조로 규격별 문서화 진행.
- **상태**: AHRI, ISO16358, KS C 9306 기초 초안 및 SASO T3 구현/검증 기록 정리 완료.
- **상세**: 완료된 문서 리스트와 세부 내역은 `project_log.md` 참조.

---

## 10. ML Pipeline 리팩토링 계획

### 10.1 현재 상태

학습 데이터 환경 확보 후 `app_trainer.py`, `app_predictor.py` 재개 예정.

### 10.2 우선 작업

- feature schema 불일치 방지 및 preprocessing 버전 관리.
- 모델 artifact 저장/로드 경로 통일.

---

## 11. UI / Calculator Window 계획

### 11.1 목표

계산 엔진과 UI를 연결하여 지역별/표준별 seasonal metric 산출 UI 제공.

### 11.2 우선 작업

- region dropdown, standard/profile 표시, 입력 폼 필터링.
- 결과 패널(SPF, load, energy, auxiliary) 및 중간값 표시.

### 11.3 주의사항

- UI 편의를 위해 엔진의 validation을 약화하지 않음.
- Core calculator는 UI와 독립적으로 검증 가능해야 함.

### 11.4 Calculator UI Refactor Plan (요약)

과거의 UI 구조 결정 및 Profile 입출력 명세 등 상세 내용은 `project_log.md` 및 `docs/architecture/project_architecture.md`를 참조할 것.

- **고정 제약**: PyQt5와 QTableView/QAbstractTableModel 기반을 유지한다. core 계산 로직, calculator public API, Train/Predict UI, 신규 그래프 의존성(matplotlib, pyqtgraph 등)은 건드리지 않는다.
- **Phase UI-1 (진행 중)**: ISO/ISEER 2점식, Hong Kong 노출. SASO T3는 이미 UI profile로 노출되어 있음. (상세보기 스크롤/그래프 개선 필요)
- **Phase UI-2**: ISO16358-2 HSPF 엔진 공통화 후 UI 연결
- **Phase UI-3 & UI-4**: EN14825 / AHRI 210/240 입력 스키마 확정 후 순차적 UI 연결
- **후속 확장 (Phase UI-5, UI-6)**: SASO T3 Multi 입력, 고급 optional matrix, UI polish (QSS 등)

---

## 12. Region Config 관리 규칙

- 규격/공식 시트 근거 필수. 임의 보정값 금지.
- JSON parse, smoke, regression(Korea 등) 필수 확인.

---

## 13. Test / Golden 관리 계획

- **golden**: 공식 시트 값 변경 시에만 expected 수정.
- **관리**: 최소 지역별 2개 이상의 golden sample 확보 권장.

---

## 14. 보류 중인 대형 리팩토링 후보

- ISO16358Calculator 분리 (HSPF 확장 후 재검토)
- common seasonal bin engine (규격 간 차이가 유지보수 문제를 일으킬 때 검토)
- UI form schema 자동 생성 (config 안정화 후 검토)

---

## 15. 가까운 실행 순서

### Step 1 — 문서 리팩토링 2차 마무리
- notes/dev/design/glossary 체계 확정 및 규격별 문서 보완.
- `docs/REFACTOR_PLAN.md`를 요약된 TODO 중심으로 유지.

### Step 2 — ISO 16358-2 HSPF 공통화
- 한국 외 국가(Hong Kong 등) HSPF 확장을 위한 공통 엔진 구현.
- `ISO16358Calculator` 내 variable-capacity heating 로직 정교화.

### Step 3 — CSPF/HSPF region config schema 전환
- `cspf_test_profile`을 포함한 통합 schema 도입.
- 기존 모든 region config(.json)를 새 schema로 마이그레이션.

### Step 4 — Calculator core 리팩토링
- region 예외 누적 시 `ISO16358Calculator` 분리 검토 (트리거 확인).
- 공통 seasonal bin engine 추상화 필요성 재판단.

### Step 5 — Calculator UI v1 마무리
- 상세 결과 graph/table 시각화 개선.
- AHRI/EN14825 탭 연결 및 입력 폼 안정화.

### Step 6 — Predictor / Calculator 연동
- ML 예측값을 Calculator 입력 schema로 자동 변환하는 pipeline 연결.
- `app_predict.py` 결과에 seasonal metric 컬럼 확장.

### Step 7 — 역방향 탐색 엔진 (MVP)
- 목표 효율 달성을 위한 하드웨어 사양 추천 로직 설계.
- 물리적 제약 조건(단조성 등)을 반영한 최적화 알고리즘 도입.

---

## 16. 삭제/폐기된 구식 계획

- “Docs 대이동” 계획: 점진적 정리로 대체.
- “엔진 완료 직후 강제 분리” 계획: 확장 예외 누적 후로 연기.
- “공통 seasonal engine 선제적 추상화”: 과설계 판단으로 폐기.

---

## 17. 한 줄 결론

검증된 계산 결과를 철저히 보존하면서, 문서 → HSPF 공통화 → Schema 전환 → UI 마무리 → ML 연동 순으로 안정화한다.

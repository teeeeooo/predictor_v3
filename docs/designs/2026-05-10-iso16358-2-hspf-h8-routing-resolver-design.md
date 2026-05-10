# ISO 16358-2 HSPF H-8 Routing and Resolver Design

## 1. Background
본 문서는 Golden Case 1~8 Diff Audit 결과와 CAL-01~08 워크북 캘리브레이션 결과를 바탕으로, ISO 16358-2 HSPF 공통 경로(Common Path)의 수식 라우팅(Routing) 및 시험점 해석(Resolver) 개선 설계를 정의한다.

- **Golden Fixture Provenance**: 현재 repo의 Golden Case 1~8은 Excel 워크북의 `Inverter AC` 시트에서 **E5="ISO 16358"** 모드로 계산된 **ISO 16358 mode workbook oracle**이다.
- **Not AS/NZS Compatibility**: 이 데이터는 AS/NZS 전용 모드나 Z-phase 호환성 참조가 아니며, 순수 ISO 16358-2 표준 수식의 워크북 구현체를 벤치마크로 한다.
- **Pure ISO Track A**: `tests/test_iso16358_hspf_pure_iso_track_a.py`는 브랜치 단위의 수식 검증 보조 도구(Verification Aid)로 유지하며, 워크북 오라클과 상호 보완 관계에 있다.

## 2. Inputs Reviewed
- `docs/iso16358/iso16358_dev_notes.md`: Section 14.1, 14.3, 14.4 (캘리브레이션 결과 및 셀 매핑)
- `tests/fixtures/iso16358_hspf_golden_fixtures.json`: Case 1~8 기대값 및 입력 풀
- `tests/test_iso16358_hspf_golden.py`: 현재 xfail/pass 상태 및 진단 헬퍼
- `core/calculator_iso16358.py`: `calculate_hspf_iso16358_common` 및 관련 수식 헬퍼 (`_iso_hspf_...`)
- `docs/REFACTOR_PLAN.md`: 공통 경로와 호환성 경로의 분리 원칙

## 3. Current Python Diff Summary
현재 구현된 Python 코드와 워크북 오라클 사이의 주요 편차 요약:

| Case | Metric | Expected (Oracle) | Actual (Python) | Diff | Remark |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Common** | **HSTL** | **4885.000** | **4885.377** | **+0.377** | Systemic Offset (Rounding) |
| Case 1 | HSEC | 1157.000 | 1156.245 | -0.755 | xfail |
| Case 2 | HSEC | 1139.000 | 1139.212 | +0.212 | **PASS** (Tolerance 이내) |
| Case 3 | HSEC | 1126.000 | 1134.088 | +8.088 | F49/F50 Routing 차이 시작 |
| **Case 4** | HSEC | 1104.000 | **1134.088** | **+30.088** | **Case 3와 동일 (2_full 무시)** |
| **Case 5** | HSEC | 1095.000 | **1134.088** | **+39.088** | **Case 3와 동일 (2_half 무시)** |
| Case 6 | HSEC | 1111.000 | 1136.557 | +25.557 | -7_ext 반영 로직 차이 |
| Case 7 | HSEC | 1117.000 | 1081.845 | -35.155 | -7_full 반영 로직 차이 |
| Case 8 | HSEC | 1111.000 | 1064.933 | -46.067 | -7_half 반영 로직 차이 |

## 4. Confirmed Facts vs Hypotheses

### 4.1. Confirmed Facts
- **Workbook Selector Structure**: B(가용성), D(Measured/Default), G/H(입력), J/K(기본값), M/N(활성값) 레이어 구조 확인.
- **Active Point Reflection**: Optional 행은 D열이 "Measured"여야만 M/N(Active)에 반영됨.
- **Exact Parity Branches**: CAL-01(Load-line), CAL-02(Cycling), CAL-08(Saturated Aux)은 규격 공식과 워크북이 정확히 일치함.
- **COP-linear Basis**: CAL-03~07을 통해 워크북이 Formula 45~50 계열의 COP 보간을 기본으로 사용함을 실증함.

### 4.2. Hypotheses
- **Frost Point Neglect**: 현재 Python `calculate_hspf_iso16358_common`이 규격 각주 d 수식을 강제 적용하면서, 입력된 `2_full`, `2_half` 측정값을 덮어쓰고 있을 것으로 추정됨. (Case 4/5 결과가 Case 3와 동일한 원인)
- **Anchor usage mismatch**: Case 7/8에서 Python이 -7°C 측정값을 직접 앵커로 사용하는 반면, 워크북은 `BE`열 등의 외삽된 중간 경계값을 우선 참조함으로써 발생하는 편차로 추정됨.

## 5. Design Boundary (Implementation Gate Candidates)

H-8의 구체적인 구현 위치 및 구조적 접근 방식은 아래 후보 중 하나를 **Implementation Gate Decision**을 통해 결정한다.

- **Candidate 1: ISO 16358-2 Common Path 보완 (Opt-in Guard)**: 
  - `calculate_hspf_iso16358_common` 내부에서 `external_calculator_minus7_fallback_override`와 같은 명시적 플래그가 활성화된 경우에만 워크북 오라클 로직이 동작하도록 설계.
- **Candidate 2: 별도 Workbook-Oracle Reproduction Profile 분리**:
  - 공통 경로 오염을 최소화하기 위해 워크북 오라클 재현을 전담하는 별도의 profile 또는 전용 helper 모듈로 로직 격리.
- **Candidate 3: Test Fixture 전용 Oracle Path 제한적 보강**:
  - 프로덕션 경로는 ISO 표준을 엄격히 고수하고, 테스트 픽스쳐 검증을 위한 별도의 벤치마크 루프에서만 워크북 관례를 보조적으로 구현.

**공통 제약 사항**:
- **Separation of Defaults**: 생산용 ISO Table 1 기본 계수(0.64 / 0.82)와 워크북 오라클용 오버라이드(0.5 / 1.105)가 코드 레벨에서 물리적으로 또는 논리적으로 절대 섞이지 않아야 함.
- **Opt-in Override**: `external_calculator_minus7_fallback_override`는 설정 파일 또는 피스쳐에 명시된 경우에만 허용됨.
- **Production Integrity**: 어떠한 경우에도 워크북 오라클 재현 로직이 생산용 기본 ISO HSPF 계산 결과에 영향을 주어서는 안 됨.

## 6. Proposed H-8 Work Units

### A. Resolved Point / Selector Trace Instrumentation
- **목적**: 구현 전, 각 Case에서 어떤 시험점이 실제로 선택(measured vs calculated)되고 보간 앵커로 쓰이는지 숫자로 고정.
- **수정 후보**: `core/calculator_iso16358.py` (내부 trace 추가), `tests/test_iso16358_hspf_golden.py` (진단 출력 강화).
- **금지**: 계산 결과 변경.

### B. 2°C Measured/Default Selector Matrix Design
- **목적**: `2_full`, `2_half` 측정값이 있을 때 각주 d에 의해 무조건 무시되지 않고, 워크북의 D열 selector처럼 "Measured" 상태를 인지하도록 리졸버 개선.
- **수정 후보**: `calculate_hspf_iso16358_common` 내의 point resolution 블록.

### C. -7°C Measured/Default/Boundary Helper Design
- **목적**: -7°C 측정값 반영 시 워크북의 `BE`/`BI`열과 유사한 외삽 경계값 관리 로직을 공통 경로에 도입.
- **수정 후보**: `_iso_hspf_capacity_curve` 및 관련 앵커 리졸버.

### D. Formula 45~50 COP-linear Routing Design
- **목적**: 현재의 capacity-linear 보간을 워크북 오라클과 일치하는 COP-linear(Formula 45~50) 방식으로 전환.
- **수정 후보**: bin loop 내의 Case B(Interpolation) 및 Case C(Saturated) 분기.

### E. Golden xfail 해소 여부 판단
- **목적**: 위 작업 완료 후 최종 오차를 확인하고 `pytest` 통과 여부 및 오차 범위(Tolerance) 확정.

## 7. Required Trace Before Implementation
구현 전 각 Case별로 수집해야 할 최소 데이터:
- **Active Point Source**: 각 단계별 measured / default / calculated / override 여부.
- **Resolved Boundaries**: 각 Bin 온도에서의 stage별 용량/전력 경계값.
- **Branch Strategy**: 각 Bin에서 선택된 수식 계열 (Cycling, F44/48, F45/49, F47/50, Saturated).
- **P_j / E_j Comparison**: 워크북 추정값과 Python 계산값의 Bin 단위 오차 상위 항목.

## 8. Stop Conditions
- CSPF Golden 결과(6.504)에 영향을 주는 변경이 감지될 경우 중단.
- KS HSPF 경로(`ks_c_9306_hspf`) 로직과 충돌하거나 해당 테스트가 실패할 경우 중단.
- 생산용 기본 계수(0.64/0.82)가 워크북 오라클 로직과 물리적으로 분리되지 못하고 강제 합쳐질 경우 중단.
- Public API의 파괴적 변경(Breaking Change)이 불가피할 경우 즉시 보고.

## 9. Next Prompt Candidates

### 1. Trace-only Instrumentation
- **목적**: 현재 `calculate_hspf_iso16358_common`의 내부 point resolution 결과를 상세히 출력하여 Case 4/5 누락을 수치로 증명.
- **금지**: 로직 수정, expected 변경.

### 2. Resolver-only Adjustment
- **목적**: 측정된 Frost 시험점이 각주 d에 의해 삭제되지 않고 "Measured" 상태를 유지하도록 리졸버 로직 최소 수정.
- **금지**: Formula 45~50 전력 라우팅 변경.

### 3. Formula-routing-only Update
- **목적**: 확정된 앵커 포인트를 바탕으로 전력 계산 방식을 COP-linear(Formula 45~50)로 전환.
- **금지**: 리졸버/피스쳐 수정.

### 4. Golden Tolerance Finalization
- **목적**: 구현 완료 후 최종 Actual 값을 보고 `pytest` 오차 수치 확정 및 xfail 해제.
- **금지**: 구현과 같은 턴에서 수행.

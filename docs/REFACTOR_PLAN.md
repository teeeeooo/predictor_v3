# Refactor Plan

## Purpose
- 리팩토링 후보와 트리거만 관리한다.
- 장기 목표와 Phase 1~5는 `PROJECT_CHARTER.md`를 따른다.
- 현재 우선순위와 다음 실행 순서는 `docs/WORK_PLAN.md`를 본다.
- 실제 작업 기록과 decision history는 `project_log.md`를 본다.
- 큰 설계 결정은 `docs/designs/*`에 둔다.

## Refactor principles
- 계산 결과 회귀 방어 최우선
- public API 무단 변경 금지
- golden expected 임의 변경 금지
- 한 번에 대규모 구조 변경 금지
- 분리 전 branch trace / tests / fixtures 보호 확인

## Active refactor candidates

### 1. Calculator series reset: 기존 ISO 파일 legacy 격하 + 새 calculator 3종 작성
- **왜 후보인지**: 기존 `core/calculator_iso16358.py`가 ISO16358, KS C 9306, AS/NZS workbook oracle trace, region compatibility, UI/profile 기대를 동시에 떠안으면서 작업이 반복적으로 꼬임. 037~043 사이클의 점진 cleanup으로는 boundary 책임이 정렬되지 않는다는 것이 확인되었다.
- **방향 전환 (2026-05-17)**: “기존 `core/calculator_iso16358.py`를 부분 cleanup으로 계속 살리는 방향”은 종료한다. 기존 파일은 legacy/reference로 격하하고, 새 ISO / KS / ASNZS calculator 3개 파일을 명확한 책임으로 재작성한다.
- **목표 boundary**:
  - `core/calculator_iso16358.py` (새 파일) — ISO 16358 CSPF/HSPF common standard logic 전용. KS / ASNZS / workbook oracle / legacy diagnostic helper 미포함. Hong Kong / India / SASO / ISO T1 default 등 ISO 16358 기반 regional profile JSON을 해석하는 대표 calculator.
  - `core/calculator_ks_c9306.py` — KS C 9306 전용 special calculator (KS CSPF, KS HSPF). `data/region_configs/korea.json`을 직접 해석. ISO calculator가 KS config를 대신 해석하지 않는다.
  - `core/calculator_asnzs_hspf_excel.py` — AS/NZS workbook oracle / Excel compatibility 전용 (Z-phase 또는 별도 compatibility phase에서 작성).
  - 기존 `core/calculator_iso16358.py`의 현 내용은 rename/archive를 통해 legacy/reference 위치(예: `core/legacy/calculator_iso16358_legacy.py`)로 격하한다. 정확한 경로/이름은 별도 audit으로 결정한다.
- **Region config 저장소**: `data/region_configs/`는 ISO 전용이 아니라 여러 calculator가 공유하는 정적 standard/region config 저장소이다. 각 JSON은 boundary에서 정한 calculator가 직접 해석한다.
- **Next work order**:
  1. 기존 `core/calculator_iso16358.py`의 legacy/reference 격하 audit (rename target 경로, import 영향, profile/dispatcher/UI/test의 직접 참조 grep).
  2. legacy 격하 실행 (rename + import 정정 + `python3 -B -m py_compile` + baseline tests 기준 회귀 없음 확인).
  3. 새 `core/calculator_iso16358.py` skeleton 작성 (책임/public API 시그니처만 표시한 빈 모듈).
  4. 새 ISO 16358 CSPF/HSPF 최소 공식 구현 (regional profile JSON 직접 해석).
  5. `core/calculator_ks_c9306.py` standalone 잔여 정리 (이미 standalone이 된 부분 외 잔여 의존 제거).
  6. AS/NZS workbook oracle은 `core/calculator_asnzs_hspf_excel.py` Z-phase compatibility calculator로 보류.
  7. profile resolver / Calculator UI 연결은 위 calculator series가 안정화된 뒤 별도 작업.
- **tests 정책 (이번 reset에 한정)**: legacy implementation behavior를 고정하는 테스트는 그대로 유지하지 않는다. 필요한 regression만 새 calculator contract 기준으로 이전하고, diagnostic / workbook-mixed 테스트는 삭제 또는 legacy/archive 디렉터리로 격리한다. 새 calculator skeleton 단계에서 해당 분류 audit을 선행한다.
- **037~043 사이클의 미세 cleanup은 종료**: KS measured input prep 분리(037), CSPF point resolution 분리(038), standalone body 구현(039), audit(040), legacy delegate 제거(041), ISO ks_intersection 분기 제거 audit(042) 및 구현(043) 같은 작업은 이번 reset 이후 더 이상 다음 작업으로 제안하지 않는다.
- **Reference branch**: `work/iso-hspf-refactor-ui-followup`은 merge 대상이 아니라 reference/spike로만 둔다. diff cherry-pick 또는 merge는 수행하지 않는다.
- **지켜야 할 guard**: public API contract와 새 calculator의 expected/golden 기준 유지. KS C 9306 region config 해석을 새 ISO common path에 합치지 않고, AS/NZS workbook oracle convention을 새 ISO common path에 섞지 않는다.

### 2. ISO CSPF/HSPF helper separation
- **CSPF/HSPF helper 분리 후보**: bin loop, point resolution, energy accumulation 등 공통 로직 모듈화. 이번 series reset 이후 새 ISO 파일 안에서 처음부터 명확한 helper 경계로 작성한다.
- **common path / region-specific path 경계**: 공통 엔진이 특정 지역의 특수 로직(예: KS C 9306)에 오염되지 않도록 분리.
- **production path와 compatibility path 분리**: 표준 경로와 호환성 경로(Z-phase)의 코드 베이스 격리.

### 3. KS C 9306 helper separation
- **KS C 9306 독립성 유지**: 한국 고유의 부하 라인 계산 및 보간 규칙을 `core/calculator_ks_c9306.py` 별도 모듈로 관리. 039 이후 KS standalone body는 이미 ISO에 의존하지 않으므로, 본 항목은 series reset 이후에도 잔여 의존 검증 단위로만 유지한다.
- **common ISO로 무리하게 흡수하지 않음**: KS C 9306은 AHRI / EN14825처럼 special calculator로 분리하며, 새 ISO calculator도 `korea.json` 같은 KS region config를 해석하지 않는다.
- **분리 트리거**: ISO 파일 legacy 격하와 새 ISO skeleton 작성 직후 잔여 audit으로 수행.

### 4. profile/schema resolver cleanup
- **region config / profile schema / calculator input boundary**: 각 레이어 간의 데이터 계약 명확화.
- **nested config 직접 주입 금지**: 계산기 core가 config 파일 구조에 직접 의존하지 않도록 resolver를 통한 데이터 전달.
- **resolver-backed path 필요성**: 신규 규격 추가 시 유연한 확장을 위한 프로필 리졸버 강화.

### 5. UI resolver-backed config selection
- **UI가 config 파일을 직접 scan하는 경로 정리 후보**: 현재 UI 계층이 리졸버 가드를 우회하여 파일을 직접 스캔하는 문제 해결.
- **calculator profile resolver 우회 방지**: UI에서도 항상 `core/calculator_profiles.py`를 통해 설정을 로드하도록 강제.

## Deferred refactor candidates
- common seasonal bin engine
- full plugin architecture
- AS/NZS HSPF compatibility calculator module
- Excel row-level exact reconstruction support
- large package split

## Not refactor tasks
- HSPF xfail 해소
- golden fixture 보강
- UI 기능 구현
- ML/inverse-search 복귀
- 문서 오타 수정
- 단순 validation/smoke test 추가

## Refactor trigger checklist
- 파일/클래스 비대화
- 같은 branch 조건이 반복적으로 생김
- common path 수정 시 region regression이 반복적으로 깨짐
- UI/config/ML schema가 calculator core에 침투함
- public API 또는 result schema가 흔들릴 위험이 생김

## Guardrails for any refactor
- public API 유지
- golden/smoke/validation test 선확인
- region config 의미 변경 금지
- compatibility calculator와 production calculator 분리
- `docs/designs/*`에 design gate summary 작성 후 구현

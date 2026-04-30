# Region Config Rules

- region config는 production 규격 데이터만 저장한다.
- golden/sample/test 전용 값은 절대 넣지 않는다.
- 테스트 fixture는 tests/fixtures/ 아래에 둔다.
- data/region_configs/*.json에 숫자를 추가/변경할 때는 출처를 주석 또는 인접 문서에 남긴다.
- 기존 region의 CSPF/HSPF 값을 바꿀 때는 해당 golden/regression test를 실행한다.

## ISO 16358-2 / HSPF Load Line Rule

- HSPF heating building load 기준 capacity는 region/profile별로 다를 수 있다.
- ISO/KS 문구상 `BLh = BLc(35) × 0.82`처럼 cooling reference가 등장하더라도, 실제 계산 시트/지역 규칙에서는 다른 입력을 사용할 수 있다.
- HSPF load line 기준 capacity는 `hspf.load_line.source`로 선언한다.
- 현재 지원 key는 `source`이다. `capacity_source`는 사용하지 않는다.
- `hspf.load_line`을 정의할 경우 `source`, `zero_load_temp`, `full_load_temp`, `rated_capacity_factor`는 모두 필수다.
- production region config에는 golden/sample/test fixture 값을 넣지 않는다.
- 예:
  - Korea / KS C 9306 HSPF: 현재 공식 계산 시트 동작 기준 `source = rated_heating_capacity`, `rated_capacity_factor = 0.82`를 사용한다. 단, spec text에는 `BLc(35) × 0.82` cooling reference가 있으므로 이 해석은 주석/문서로 유지한다.
  - Australia / New Zealand: AS/NZS 3823.4.2 원문 확인 전까지 load line source 임의 구현 금지.
- production region config에는 원문/공식 계산 시트 근거가 없는 load line 값을 넣지 않는다.

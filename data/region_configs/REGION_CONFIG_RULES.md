# Region Config Rules

- `data/region_configs/`는 ISO16358 전용 저장소가 아니라, 여러 calculator가 공유하는 정적 standard/region config 저장소이다. calculator code에 하드코딩하지 않을 standard constants / bin hours / test point rules / load-line metadata / derived factor 같은 정적 데이터를 한 곳에 모은다.
- 각 JSON은 한 calculator가 직접 해석한다. ISO16358은 Hong Kong / India / SASO / ISO T1 default 등 ISO 16358 기반 regional profile JSON을 해석하고, KS C 9306 calculator는 `korea.json`을 직접 해석한다 (ISO common path가 해석하지 않는다). AHRI calculator는 `usa.json`, `usa_hspf2.json`을 해석한다.
- AS/NZS workbook oracle compatibility는 ISO common path에 섞지 않고 별도 opt-in compatibility calculator/profile로 다룬다. 해당 config도 이 폴더에 둘 수 있으나 ISO common config와 schema/해석 경로를 섞지 않는다.
- region config는 production 규격 데이터만 저장한다.
- golden/sample/test 전용 값은 절대 넣지 않는다.
- 테스트 fixture는 tests/fixtures/ 아래에 둔다.
- data/region_configs/*.json에 숫자를 추가/변경할 때는 출처를 주석 또는 인접 문서에 남긴다.
- 기존 region의 CSPF/HSPF 값을 바꿀 때는 해당 golden/regression test를 실행한다.
- Phase 1 production config와 Phase 2 planned config를 구분한다.
- production region config에는 sample/golden/test 전용 값을 넣지 않는다.
- source golden과 current-engine regression이 다를 경우 production config를 golden에 맞추기 위해 Cd, bin, derived factor를 임의 변경하지 않는다.
- source golden은 xfail 또는 reference note로 보존하고, 원인 분석 후 공식 계산기 구조 차이가 확인되면 docs/REFACTOR_PLAN.md에 등록한다.
- official xlsx compatibility 옵션은 region config에 opt-in으로 명시하고, 다른 region 기본 동작을 바꾸지 않는다.
- SASO T3는 cspf_profile schema Phase R2 전까지 production config로 강제 편입하지 않는다.

## Config Location / Promotion Rule

- production 또는 regression test의 primary config로 승격된 JSON은 `data/region_configs/` 하위에 둔다.
- 실험/scaffold JSON이 테스트 primary fixture 또는 production config로 승격되면, 다음 중 하나를 반드시 수행한다.
  - `data/region_configs/` 하위로 이동하고 코드/테스트/문서 참조를 갱신한다.
  - 즉시 이동할 수 없으면 예외 사유와 후속 TODO를 `docs/REFACTOR_PLAN.md` 또는 관련 dev_notes에 기록한다.
- 같은 region/standard의 cooling/heating config를 통합할 때는 기존 calculator가 기대하는 schema를 먼저 확인한다.
- AHRI SEER2/cooling은 `data/region_configs/usa.json`, AHRI HSPF2/heating은 `data/region_configs/usa_hspf2.json`을 사용하며 현재 flat schema가 달라 단순 병합하지 않는다.
- top-level key(`bin_data`, `test_point_temps`, `constants`, `defaults`)의 의미가 mode별로 다르면 단순 병합하지 않는다.
- 완전 통합은 `cooling` / `heating` namespace 또는 loader compatibility가 준비된 뒤 수행한다.

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

# Region Config Rules

- region config는 production 규격 데이터만 저장한다.
- golden/sample/test 전용 값은 절대 넣지 않는다.
- 테스트 fixture는 tests/fixtures/ 아래에 둔다.
- data/region_configs/*.json에 숫자를 추가/변경할 때는 출처를 주석 또는 인접 문서에 남긴다.
- 기존 region의 CSPF/HSPF 값을 바꿀 때는 해당 golden/regression test를 실행한다.
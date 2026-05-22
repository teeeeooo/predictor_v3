# ISO16358 초기 리버스 엔지니어링 보관 자료

## Status

- 이 폴더는 historical archive / initial reverse-engineering snapshot입니다.
- 현재 production runtime, tests, calculator path에서 import하지 않습니다.
- 이 파일들은 당시 분석 맥락 보존용이며 active calculator implementation source가 아닙니다.
- 삭제 / 이동 / rename은 별도 archive cleanup decision 없이는 하지 않습니다.
- 최신 ISO16358 calculator 상태는 active docs, `docs/WORK_PLAN.md`, relevant tests를 따릅니다.

이 폴더는 ISO16358-1 AMD1 공식 Excel 계산 도구를 분석하던 초기 단계의 일회성 스크립트와 수식 추출 결과를 보관하기 위한 위치입니다.

이 파일들은 현재 production 계산 경로가 아닙니다.

현재 기준 계산 로직은 아래 파일들을 기준으로 합니다.

- `core/calculator_iso16358.py`
- `data/region_configs/`
- `tests/test_iso16358_*`

이 보관 자료를 현재 동작의 source of truth로 사용하지 마세요.
이 파일들은 초기 구현 과정과 계산식 추적을 위한 이력 보존 목적으로만 유지합니다.

# 096 ISO16358-2 HSPF frost trace patch

## Goal
ISO16358-2 HSPF common 계산의 bin detail에서 frost flag가 명시적으로 출력되도록 수정한다. case 8 / case 16에서 tj=-1, tj=0 bin이 trace 추출 단계에서 frost=False로 잘못 해석되던 문제를 해소한다.

## Scope / Non-goals
- Scope: `_iso_hspf_evaluate_common_bin()`의 detail 출력에 `frost` 필드 명시 추가, frost boundary focused 테스트 추가.
- Non-goals: Formula 44/45/47/48/49/50 계산식 수정, expected/fixture/xfail 수정, branch/case naming, ISO table UI 작업, lifecycle maintenance, AHRI/EN/UI 변경.

## task 1 결과
- 수정 파일: `core/calculator_iso16358.py`
- 변경 위치: `_iso_hspf_evaluate_common_bin()` (대략 L1493 이후).
  - 기존 frost 판단식 (`frost_lower < tj < frost_upper`, `lower=-7.0`, `upper=5.5`)을 유지.
  - 반환 `detail` 딕셔너리에 `"frost": frost`를 명시적으로 포함.
  - `detail.update(branch_result["trace"])` 이후 한 번 더 `detail["frost"] = frost`를 적용해 branch trace dict에 우연히 들어올 수 있는 frost 키가 명시 값을 덮어쓰지 않도록 보장.
- 계산식 변경 없음. branch 선택 / Formula 호출 경로 / capacity·power curve / load line 전부 그대로.

## task 2 결과
- `compare_iso16358_hspf.py`, `extract_bin_trace`, frost trace helper를 repo 전체에서 검색 (`rg` / `find`).
- 결과: repo에 해당 스크립트 / helper 부재. 수정 대상 없음 → repo에 없음, 수정 생략.

## task 3 결과
- 신규 파일: `tests/test_iso16358_hspf_frost_trace.py`
- 내용: `test_iso_hspf_common_bin_exposes_frost_flag`를 `pytest.parametrize`로 다음 boundary를 검증.
  - tj=-10 → frost False
  - tj=-7 → frost False
  - tj=-6 → frost True
  - tj=-1 → frost True
  - tj=0 → frost True
  - tj=5 → frost True
  - tj=5.5 → frost False
  - tj=6 → frost False
- 기존 `tests/test_iso16358_hspf_formula_micro.py`의 helper (`make_iso_micro_calculator`, `iso_points_with_extended`, `rated_for_load_at_7c`) 만 재사용하여 최소 config / 최소 measured input으로 common 경로를 통과.
- case 8, case 16 expected / official exact fixture / xfail 목록은 건드리지 않음.

## task 4 결과
- `docs/WORK_PLAN.md` "Repo 다음 순서" sequence를 갱신.
  - 1: ISO16358-2 HSPF Formula 44/45/47/48/49/50 boundary COP alignment (외부 분석 결과 도착 후 진행)
  - 2: ISO table Excel-like behavior patch
  - 3: ISO result/read-only table copy TSV
  - 4: unit adapter 확장 (ISO / KS / EN)
  - 5: ML / inverse-search 복귀 준비
  - 추가 메모: 096에서 frost flag trace 노출 수정 완료, ISO16358-2 HSPF 전체 mismatch는 여전히 외부 분석 대기 hold.
- result_reports active/archive/summaries 이동 및 `project_log.md` lifecycle 정리는 이번 범위에서 제외. 사용자 지시상 trace 출력 보정만 수행하며 lifecycle maintenance는 별도 작업이기 때문.

## Verification
- `python3 -B -m py_compile core/calculator_iso16358.py` → OK
- `python3 -B -m pytest tests/test_iso16358_hspf_frost_trace.py -q` → 8 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_official_exact_golden.py tests/test_calculator_schema_boundaries.py -q` → 58 passed, 11 xfailed (xfail 목록 유지)
- `python3 -B -m pytest -q` → 405 passed, 3 skipped, 34 xfailed

## Known Risks
- ISO16358-2 HSPF case 8/16을 포함한 mismatch는 사용자 외부 분석 대기 hold 상태로 그대로 둠. 본 패치는 trace 출력의 frost 필드를 명시적으로 노출했을 뿐 계산값 자체는 변하지 않는다.
- result_reports lifecycle maintenance pending: active 폴더에 095까지 누적되어 있어 향후 archive/summaries 정리가 필요하지만 이번 범위에서는 수행하지 않음.

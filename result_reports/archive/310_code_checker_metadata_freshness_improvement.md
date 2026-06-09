# Report 310: Code Checker Metadata & Freshness Check Improvement

## Goal

- `tools/code_checker` reference map 생성물에 compact metadata(Git commit, dirty 여부, generated_at_utc 등) 및 freshness 판단 메커니즘을 추가하여 map 관리 도구를 고도화한다.
- `CODEBASE_REFERENCE_MAP.md`를 이번 작업에서 직접 재생성하지 않으며, freshness 판정을 non-hard-gate warning-first로 구축한다.

## Scope

### Included Changes

- `tools/code_checker/metadata.py` 신설: Git commit short hash, dirty working tree status 수집, metadata HTML 주석 렌더링, parsing, freshness status 평가(fresh, stale, metadata_missing) 구현.
- `tools/code_checker/renderer.py` 수정: `render_compact_map` 함수가 metadata 딕셔너리를 전달받아 헤더 바로 위에 HTML comment로 주입하도록 확장.
- `tools/code_checker/build_reference_map.py` 수정: CLI 옵션(`--check` 및 `--output`) 파싱 추가, `build_map` 연동 및 read-only freshness check 기능 연결.
- `tests/test_code_checker_reference_map.py` 수정: metadata 생성/렌더링 및 parsing/freshness 검증을 위한 2개의 focused test 추가.
- `docs/WORK_PLAN.md` 및 `project_log.md` 갱신.

### Excluded Scope

- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성 및 수동 변경 금지.
- ML/Predictor, calculator core 및 UI(ui_tk) 계층 코드 수정 금지.
- `tools/check_code_structure.py` 규칙 수정 금지.
- hard gate (예: pre-commit hook 강제 등) 및 CI 빌드 실패 판정 도입 금지.
- active report lifecycle cleanup 보류.

## Verification

- `python3 -B -m py_compile tools/code_checker/*.py` 컴파일 성공 확인.
- `python3 -B -m pytest tests/test_code_checker*.py -rs -vv` 11개 테스트 모두 통과 (2개 신규 focused test 포함).
- `python3 -B tools/code_checker/build_reference_map.py --check` 실행 결과 `METADATA_MISSING` status 확인 (hard-fail 없이 0 종료).
- `python3 -B tools/check_code_structure.py` (warnings: 4 pre-existing, 0 new) 통과.
- `git diff --check` 및 `git status --short` 확인 완료.

## Reference Evidence Gate & Wording Policy

- **Warning-First / Non-Hard-Gate**: code_checker는 구조 및 참조 evidence tool이므로 freshness check 결과가 stale이어도 warning text만 출력하고 hard fail하지 않음.
- **Metadata Format**: 마크다운 최상단에 hidden HTML comment로 주입 (`<!-- CODE_CHECKER_METADATA: {"generator": "code_checker", "schema_version": "1.0.0", "git_commit_short": "...", "git_dirty": ..., "generated_at_utc": "..."} -->`).

## Active Report Count

- active report count exceeds lifecycle threshold; cleanup pending.

## Lifecycle Maintenance Note

- **Pending**: 이번 작업은 lifecycle cleanup이 아니며, active report 갯수가 임계값(10)을 초과하였으나 cleanup은 pending 상태로 유지하고 추후 별도 follow-up 작업으로 처리함.

## Next Suggested Action

1. **Regenerate reference map and commit milestone changes**
2. **Controller switch arc final summary / closeout**
3. **Active report lifecycle cleanup**
4. **Main table migration check**
5. **ui_tk folder cleanup**
6. **EN14825 / AHRI 210/240 / KS profile expansion**

## Commit / Push

- Commit command: `git commit -m "docs/tools: Add code checker metadata freshness support"` (no-verify 사용 금지)
- Pushed successfully.

# Report 309: Reference Evidence Gate Warning-First Workflow Patch

## Goal

- Reference Evidence Gate를 warning-first workflow로 보정하여 코드 수정 전 preflight 자문 checklist(책임/surface 추가, 중복, 우회, 핫스팟 확장 여부)를 도입한다.
- 영구 문서(durable docs)와 리포트 본문 내 exact active report count를 기재하지 않는 wording policy를 추가하고, 기존 exact count를 threshold wording으로 교정하여 count 불일치 문제를 근본적으로 해결한다.

## Scope

### Included Changes

- `docs/agent_workflows/DIFF_READ_BUDGET.md`의 Reference Evidence Gate 안내와 warning-first checklist(책임/surface 추가, 중복, 우회, 핫스팟 확장 여부) 추가.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` 내 active report count wording policy 추가.
- `AGENT_TASK_ROUTER.md` 라우팅 문구 보정.
- `docs/WORK_PLAN.md` 갱신 및 기존 exact count 변경.
- `project_log.md` 및 `result_reports/active/308_post_saso_t3_controller_switch_validation_gui_smoke_closeout.md`, `result_reports/active/306_align_305_code_checker_audit_with_original_intent.md` 내 exact count 변경.

### Excluded Scope

- Python 코드 수정 금지.
- `tools/code_checker` 기능 수정 및 map regeneration 금지.
- `tools/check_code_structure.py` 수정 금지.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성 금지.
- 이번 슬라이스에서의 active report lifecycle cleanup (파일 이동/아카이빙) 보류.

## Verification

- `python3 -B tools/check_code_structure.py` 실행 완료.
- `git diff --check` 및 `git status --short` 확인 완료.
- active report count 검증 완료 (exact count는 final terminal output으로만 출력).

## Reference Evidence Gate & Wording Policy

- **Warning-First Checklist**: 새 책임/surface 추가, 중복 logic, owner 우회, 핫스팟 확장 여부 모두 No일 경우 복잡한 preflight 없이 scoped 작업 바로 진행. code_checker는 reference/structure evidence이며 hard guard는 기존 check_code_structure.py가 소유.
- **Wording Policy**: durable docs 및 리포트 본문에는 exact active report count 대신 `active report count exceeds lifecycle threshold; cleanup pending`과 같은 threshold wording만 표기하여 리포트 생성 전후의 count 불일치 방지.

## Active Report Count

- active report count exceeds lifecycle threshold; cleanup pending.

## Lifecycle Maintenance Note

- **Pending**: 이번 작업은 lifecycle cleanup이 아니며, active report 갯수가 임계값(10)을 초과하였으나 cleanup은 pending 상태로 유지하고 추후 별도 follow-up 작업으로 처리함.

## Next Suggested Action

1. **code_checker metadata & freshness check improvement**
2. **Regenerate reference map and commit milestone changes**
3. **Controller switch arc final summary / closeout**
4. **Active report lifecycle cleanup**
5. **Main table migration check**
6. **ui_tk folder cleanup**
7. **EN14825 / AHRI 210/240 / KS profile expansion**

## Commit / Push

- Commit command: `git commit -m "docs: Patch warning-first reference evidence workflow"` (no-verify 사용 금지)
- Pushed successfully.

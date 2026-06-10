# Report 341: Align Post-Batch-Foldering Next Action

## Goal (목표)

- 340 Batch foundation foldering Slice 2 완료 후 Next Action이 현재 확정된 장기 구조 방향과 맞지 않는 문제를 발견하여, WORK_PLAN 및 340 report 내 차기 과제를 올바른 방향으로 정렬하고 보정한다.

## 발견된 Next Action Mismatch

- 340 Slice 2 완료 시점의 WORK_PLAN과 340 report는 다음 작업을 `Calculator entrypoint handover from PyQt to Tkinter`로 두고 있었음.
- 그러나 사용자가 확정한 장기 구조 목표는 `apps/{calculator,train,predict}/` 패키지 아키텍처임.
- 이에 따라 calculator entrypoint handover를 성급하게 수행하기보다, `Apps package architecture audit`을 선행하는 것이 안전하고 적합함.

## 사용자 확정 판단 (User Alignment)

- **장기 구조 목표**: `apps/{calculator,train,predict}/`
- **PyQt UI**: 현재 `ui/`는 legacy PyQt multi-app UI로 유지되며, 차후에 버리거나 새로 작성될 예정임.
- **Tkinter UI**: 현재 `ui_tk/`는 calculator-only Tkinter UI이며, 장기적으로 `apps/calculator/ui/` 하위로 이동하는 구조가 타당함.
- **선행 조치**: `app_calculator.py` handover 전에 apps package boundary 및 `app_train.py` / `app_predict.py`를 아우르는 train/predict app boundary까지 종합 고려하는 Audit을 먼저 수행해야 함.
- **Batch foldering의 의의**: `ui_tk` 내부 구조 정리를 통해 향후 `apps/calculator/ui/` 하위로의 이주(move)를 매우 수월하게 만드는 토대를 마련함.

## WORK_PLAN 보정 내용 (WORK_PLAN alignment)

- `docs/WORK_PLAN.md`의 Next Actions 섹션 내 차기 과제를 다음과 같이 수정함:
  1. **Apps package architecture audit before calculator entrypoint handover**
  2. **Calculator entrypoint handover from PyQt to Tkinter**
  3. **ui_tk root folder inventory audit, or merge into apps architecture audit if ownership overlap is confirmed**
  4. **EN14825 / AHRI 210/240 / KS profile expansion**

## 340 Report 보정 내용 (Report 340 alignment)

- `result_reports/active/340_batch_foundation_foldering_slice_2_views_controllers.md` 내 `WORK_PLAN 업데이트 여부` 및 `Next Action suggested` 항목을 보정하여 `Apps package architecture audit`이 선행되어야 함과 그에 따른 세부 맥락(long-term target이 `apps/{calculator,train,predict}/`라는 점, `ui_tk/`와 legacy `ui/`의 역할 차이)을 기술하도록 업데이트함.

## 변경하지 않은 범위 (Excluded Scope)

- **소스 코드 수정 없음**: production Python source, tests, ui_tk 코드의 실제 수정 없음.
- **파일 구조 변경 없음**: apps 폴더 생성, 파일 이동/rename, import path 수정 없음.
- **기타 문서 수정 없음**: `docs/code_map/CODEBASE_REFERENCE_MAP.md` 수정 또는 regeneration 수행하지 않음. `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged).

## 검증 결과 (Verification Results)

- `python3 -B tools/check_code_structure.py` 통과 (OK)
- `git diff --check` 상의 whitespace 문제 없음 (OK)
- `git status --short` 확인 결과 허용된 3개 파일(docs/WORK_PLAN.md, 340 report, 신규 341 report) 외의 변경 사항 없음 확인 (OK)

## Project Memory Delta

- none

## Lifecycle Note

- active report count is below lifecycle threshold

## Next Action suggested (차기 과제)

1. **Apps package architecture audit before calculator entrypoint handover**

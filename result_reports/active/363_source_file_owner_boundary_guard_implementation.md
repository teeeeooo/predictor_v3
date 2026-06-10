# Active Report 363: Source File Owner Boundary Guard Implementation

## 목표 (Goal)
* 362에서 설계한 Source File Owner Boundary Policy를 바탕으로 `tools/check_code_structure.py`에 정적 검사기(guard) 규칙을 구현하고, 새로운 가드들이 정상 작동하는지 unit test로 검증한다.
* `PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` 내의 로컬 절대 경로 링크(`file:///Users/...`)를 repo-relative code path 표기로 고쳐 타 환경에서의 깨짐 문제를 해결한다.
* 이번 작업은 guard 구현 및 문서 보정 slice이며, 기존 소스 이동/리팩토링 등은 수행하지 않는다.

## 수정 파일 (Modified Files)
* [tools/check_code_structure.py](../check_code_structure.py): 5가지의 신규 owner boundary guard 구현 및 run_checks() 통합
* [tests/test_code_structure_guard.py](../../tests/test_code_structure_guard.py): 각 가드 규칙들에 대응하는 5개 focused unit tests 추가
* [docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md](../../docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md): Good example 링크를 absolute URL에서 relative code path로 수정
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): 작업 완료 기록 반영 및 Next Actions 조율

## Guard 구현 내용 및 Error/Warning 구분 (Guard Implementation)
`tools/check_code_structure.py`에 구현 및 연동한 정적 가드 규칙들은 다음과 같습니다:

1. **`check_ui_root_flat_feature_file`** (`error`):
   * `apps/calculator/ui/` root 바로 아래에 피처 특정 flat 파일(예: `en14825_*.py`, `saso_*.py` 등)의 생성을 방지합니다.
   * 위반 시 `error`로 분류되어 빌드/검사 프로세스를 실패 처리(exit code 1)합니다.
2. **`check_sections_flat_model_adapter_table`** (`error`):
   * `apps/calculator/ui/sections/` 바로 아래에 피처 특정 model, adapter, table model (예: `*_adapter.py`, `*_models.py` 등)이 dumping되는 것을 방지합니다.
   * 위반 시 `error`로 분류됩니다.
3. **`check_core_root_flat_helper_misc_utils`** (`warning`):
   * `core/` root 바로 아래에 `*_helper.py`, `*_misc.py`, `*_utils.py` 등의 보조용 flat file이 신규 부채로 추가되는 것을 탐지합니다.
   * warning-first 정책에 따라 위반 시 `warning`을 출력하되 검사 자체를 실패하게 만들지는 않습니다.
4. **`check_tests_mega_test_naming`** (`warning`):
   * `tests/` 아래에 `test_*_everything.py` 또는 `test_*_all.py` 와 같이 무분별하게 합쳐진 mega-test 생성을 경고하고 focused tests 구성을 유도합니다.
   * 위반 시 `warning` 처리됩니다.
5. **`check_ui_package_registry`** (`warning`):
   * `apps/calculator/ui/` 하위에 새로운 서브 디렉토리가 추가되는 경우, 허용된 package registry(`batch`, `batch_dialogs`, `en14825`, `sections`, `table`, `tabs`)에 속해 있는지 대조 검사합니다.
   * 임의 디렉토리 생성 감지 시 `warning`으로 경고하여 패키지 등록을 유도합니다.

## Focused Tests 추가
[tests/test_code_structure_guard.py](../../tests/test_code_structure_guard.py) 파일에 다음의 순수 단위 테스트 케이스를 추가하여 검출 의도를 확실하게 고정했습니다:
* `test_check_ui_root_flat_feature_file`: `en14825_seer_adapter.py` 생성 시 `error` 탐지 및 정상 파일 패스 확인.
* `test_check_sections_flat_model_adapter_table`: `sections/en14825_seer_table_model.py` 생성 시 `error` 탐지 및 정상 section 뷰 패스 확인.
* `test_check_core_root_flat_helper_misc_utils`: `core/new_standard_utils.py` 생성 시 `warning` 탐지 및 calculator 파일 패스 확인.
* `test_check_tests_mega_test_naming`: `tests/test_newstandard_everything.py` 생성 시 `warning` 탐지 및 focused test naming 패스 확인.
* `test_check_ui_package_registry`: `new_unregistered_package/foo.py` 추가 시 `warning` 탐지 및 등록된 패키지/플랫 파일 패스 확인.

## 구현하지 않은 Guard 후보 (Deferred Candidates)
* 모든 가드 규칙 후보가 100% false positive 없이 동작하며 error/warning으로 적절히 나누어 성공적으로 구현되었습니다. 따라서 미뤄진(deferred) guard candidate는 없습니다.

## 아키텍처 규칙 변경 사항 요약 (Metadata/Scope Changes)
* **Source Moves**: 없음 (기존 소스 이동/rename 없음).
* **Source Changes**: `tools/check_code_structure.py`만 수정되었으며, 테스트/문서/작업 로그만 보강되었습니다.
* **Fixture/Golden/Schema/Public API Changes**: 없음.
* **Manual Check 필요 여부**: 없음 (자동 guard 및 pytest로 완전히 제어됨).

## 검증 결과 (Verification Results)
* `python3 -B -m py_compile tools/check_code_structure.py`: **OK**
* `python3 -B -m pytest tests/test_code_structure_guard.py -q`: **29 passed** (기존 24개 + 신규 5개)
* `python3 -B tools/check_code_structure.py`: **code structure guard: OK (no findings)** (현재 repo가 새로운 strict guard를 정상 통과함)
* `git diff --check`: whitespace 에러 없음.

## Next Action
* **Active report lifecycle cleanup** (16개의 active report가 쌓여 있으므로 summaries/archive 정리 실행).

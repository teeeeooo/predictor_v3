# Active Report 358: EN14825 GUI Contract Correction

## 목표 (Goal)
* 9e32d42에서 작성한 EN14825 declared/tested GUI design contract의 세부 계약과 로컬 경로 및 report 번호 중복 오류를 보정한다.
* 이번 작업은 documentation correction 전용이며, production source, tests, apps/calculator/ui 구현은 수정하지 않는다.

## 보정한 design contract 항목 (Corrected Details)

### 1. Local absolute file links 제거
* design contract 내에 포함되어 있던 로컬 절대 경로 링크(`file:///Users/sunjaekim/Downloads/태우 작업/...`)들을 repo-relative 상대 경로 링크(예: `../../apps/calculator/ui/`)로 보정하였습니다.
* 타 환경에서의 링크 깨짐을 방지하고 로컬 사용자 절대 경로 정보 노출을 제거하였습니다.

### 2. SCOP Tbiv/TOL defaults 및 user-editable 계약 보정
* SCOP climate-specific auxiliary defaults를 다음 확정값으로 보정하였습니다:
  * **Average**: Tbiv = -10°C, TOL = -11°C
  * **Warmer**: Tbiv = 2°C, TOL = -11°C
  * **Colder**: Tbiv = -15°C, TOL = -22°C
* 이 값들은 prefill 용도의 **user-editable UI defaults**임을 명시하고, 사용자가 수정한 현재 UI 값이 core로 전달되어야 함을 못박았습니다. (기존 config의 `tbiv_max_c`, `tol_max_c`를 default로 해석하는 오류 배제)

### 3. SCOP A/B/C/D conditions 계약 보정
* SCOP A/B/C/D outdoor dry-bulb conditions를 EN14825 규격 확정 조건으로 명시하였습니다:
  * **A** = -7°C, **B** = 2°C, **C** = 7°C, **D** = 12°C
* TOL/Tbiv 온도는 fixed schema value가 아니라 climate default + user override 값임을 정리하고, guide card와 condition row가 이 resolved values를 표시하도록 계약을 정의하였습니다.
* guide card에서 symbolic meaning 설명 위주의 glossary 카드 성격을 배제하고 indoor condition note도 삭제하였습니다.

### 4. final SEER/SCOP % threshold 보정
* Final SEER % 및 SCOP %의 red threshold 기준을 기존 standard tolerance에서 **92% 미만**으로 확정하였습니다.
* 92% 이상일 때만 normal/pass-tinted cell로 표시하고, upper bound는 적용하지 않습니다.
* OK/NG text row나 final pass/fail labels 추가 금지 규정을 유지하였습니다.

### 5. visual style / architecture direction 보정
* EN14825의 visual style이 polished UI로 개선될 수 있음을 인정하되, 기존 `apps/calculator/ui` 아키텍처 패턴(section owner, thin adapter boundary, reusable table/result components, existing layout token reuse)을 엄격하게 준수해야 함을 명문화하였습니다.
* 새로운 dashboard framework나 독립 visual system 도입을 금지하고 hardcoded palette 추가를 금지하였습니다.
* EN14825 style의 타 profile reverse rollout은 future work로 제한하였습니다.

### 6. report 번호 중복 보정
* `result_reports/active/` 내에 356번 번호가 중복되어 존재하던 문제를 파악하고, EN14825 design contract report를 `357_en14825_declared_tested_gui_design_contract.md`로 rename(`git mv`)하고 내부 356 번호 reference 및 `docs/WORK_PLAN.md`를 보정하였습니다.

## 변경하지 않은 범위 (Non-goals)
* production Python source 및 tests 수정 없음.
* EN14825 GUI 및 batch 실제 구현 없음.
* data/region_configs 수정 없음.
* docs/code_map/CODEBASE_REFERENCE_MAP.md 수정 없음.

## WORK_PLAN 업데이트 여부
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md)의 Recent History에 357번(design contract 완료) 및 358번(보정 작업 완료) 항목을 추가하고, Next Actions를 최신 상태로 유지하였습니다.

## 검증 결과 (Verification Results)
* `git status --short`: `docs/WORK_PLAN.md` 수정, `docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md` 수정, report rename 및 새 358 report 추가 확인 완료.
* `python3 -B tools/check_code_structure.py`: 실행 결과 이상 없음.
* `git diff --check`: whitespace 에러 없음.

## Next Action
* **EN14825 SEER data model/table model/adapter** 구현 및 테스트/검증.

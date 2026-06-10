# Active Report 359: EN14825 Defaults Hierarchy Contract Correction

## 목표 (Goal)
* EN14825 declared/tested GUI design contract의 Open Questions에 남아 있던 defaults hierarchy 모순을 즉시 보정하여 확정된 UI default 계약과의 충돌을 해소한다.
* 이번 작업은 documentation correction 전용이며, production source, tests, apps/calculator/ui 구현은 수정하지 않는다.

## 수정한 모순 (Conflicts Resolved)
* design contract의 Open Questions / Decisions Needed 섹션에 남아 있던 "Config-derived defaults are authoritative" 취지의 문구를 삭제 및 보정하여, config 파일이 UI defaults를 완전히 덮어쓴다는 잘못된 설계를 바로잡았습니다.
* config 파일(`en14825_scop.json`, `eu.json`)의 `tbiv_max_c`, `tol_max_c`를 UI prefill defaults로 취급한다는 오해의 소지를 제거하였습니다.

## 보정된 defaults hierarchy 계약 (Corrected Defaults Hierarchy Contract)
* **명시적 UI default 소유**: EN14825 GUI는 config로부터 맹목적으로 UI default를 유도하지 않고 명시적인 UI default 계약을 사용합니다.
* **SCOP A/B/C/D 조건**: A = -7°C, B = 2°C, C = 7°C, D = 12°C 조건은 config/schema 기준 확정 고정 값입니다.
* **SCOP Tbiv/TOL prefill defaults**:
  * **Average**: Tbiv = -10°C, TOL = -11°C
  * **Warmer**: Tbiv = 2°C, TOL = -11°C
  * **Colder**: Tbiv = -15°C, TOL = -22°C
* **User-Editable**: 이 prefill defaults는 완전한 사용자 수정 가능 값이며, core 계산 시에는 default가 아니라 현재 UI에 설정된 사용자의 수정 값이 전달됩니다.
* **Config의 역할 제한**: config의 `tbiv_max_c`/`tol_max_c`는 validation limits 또는 metadata로만 활용될 뿐, UI prefill default로 사용되지 않습니다.
* **통합 정책**: 향후 어떠한 config/default merge 정책이 추가되더라도 위의 명시적인 UI default 계약은 보존되어야 합니다.

## 수정 파일 (Modified Files)
* [docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md](../../docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md)
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md)

## 변경하지 않은 범위 (Non-goals)
* production Python source 및 tests 수정 없음.
* EN14825 GUI 및 batch 실제 구현 없음.
* data/region_configs 수정 없음.
* docs/code_map/CODEBASE_REFERENCE_MAP.md 수정 없음.

## 검증 결과 (Verification Results)
* `git status --short`: `docs/WORK_PLAN.md` 수정, `docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md` 수정, 새 359 report 추가 확인 완료.
* `python3 -B tools/check_code_structure.py`: 실행 결과 이상 없음.
* `git diff --check`: whitespace 에러 없음.

## Next Action
* **EN14825 SEER data model/table model/adapter** 구현 및 테스트/검증.

# 098 ISO16358-2 HSPF remaining mismatch root-cause audit

## Goal
ISO16358-2 HSPF official exact diagnostic의 남은 11개 mismatch case에 대해 root cause를 좁히고, 다음 작업이 (a) 원문 audit인지 (b) targeted patch인지 결정한다.

## Scope
- audit-only. 코드/expected/fixture/xfail 미수정.
- 확인 대상: `tests/test_iso16358_hspf_official_exact_golden.py`, `tests/fixtures/iso16358_hspf_official_exact_cases.json`, `core/calculator_iso16358.py`의 ISO16358-2 HSPF 관련 함수, 096/097 report.
- per-bin trace는 휘발성 Python snippet으로 확인하고 repo에는 남기지 않음.

## Non-goals
- 계산식 수정, expected 수정, fixture 수정, xfail 해제, branch/case naming 변경, trace schema 표준화, UI 작업, adapter/unit, ML, lifecycle maintenance, 영구 comparison framework 추가.

## Current confirmed facts
- bin_hours total = 2866 h (27 bin), HSTL = 4885.4 kWh: 모든 16개 case에서 일치.
- 096: bin detail에 frost flag 명시 노출 완료.
- 097: Formula 44/45/47/48/49/50 보간 방향 정렬은 rewrite-only, numeric 변화 없음.
- 외부 fixture와 repo fixture point pool 동일 (-7_ext=1700/1300, 2_ext=4200/1700, 2_full=2800/800, 2_half=1500/300 등).
- `_iso_hspf_resolve_common_points()`: 측정 `2_{stage}` 입력은 `2_{stage}_f` (frost용) 키에 보존되고, `2_{stage}` 키 자체는 항상 `-7→7` 비frost 보간점으로 덮어쓰여 frost curve와 non-frost curve가 분리된다. (091/096 결론 그대로)
- non-frost extended branch (Formula 47) 는 `7_ext` AND `-7_ext` 둘 다 있을 때만 활성화. official 16-case는 `7_ext`를 입력하지 않으므로 Formula 47이 발동되지 않는다. 따라서 남은 mismatch는 전부 frost 경로 (Formula 49/50, saturated) 안에서 발생한다.

## Current diagnostic status (work/iso-separation-plan @ HEAD)
실행: `tests/test_iso16358_hspf_official_exact_golden.py` → 6 passed / 11 xfailed.
| case | repo HSEC | exp HSEC | Δ | branches | notes |
|------|-----------|----------|---|----------|-------|
| 1  | 1079.3 | 1079.3 | 0 | cycling/49/45/saturated | match |
| 2  | 1061.4 | 1061.4 | 0 | +min_half | match |
| 3  | 1079.3 | 1079.0 | +0.3 | +formula50 | xfail (small) |
| 4  | 1061.4 | 1061.1 | +0.3 | +formula50,+min | xfail (small) |
| 5  | 1079.3 | 1079.3 | 0 | -7_ext measured만 | match |
| 6  | 1077.2 | 1077.2 | 0 | -7_full measured만 | match |
| 7  | 1080.7 | 1080.7 | 0 | -7_half measured만 | match |
| 8  | 1078.5 | 1077.2 | +1.3 | -7 전부 측정, ext 없음 | xfail |
| 9  | 1058.7 | 1058.0 | +0.7 | +ext+min+formula50 | xfail (small) |
| 10 | 1064.7 | 1064.4 | +0.3 | +ext+min+formula50 | xfail (small) |
| 11 | 1061.8 | 1061.1 | +0.7 | +ext+min+formula50 | xfail (small) |
| 12 | 1111.8 | 1079.0 | **+32.8** | +ext+2_full measured | xfail (large) |
| 13 | 1077.5 | 1079.0 | -1.5 | +ext+2_half measured | xfail |
| 14 | 1077.5 | 1079.0 | -1.5 | same as 13 (dup) | xfail |
| 15 | 1116.0 | 1079.0 | **+37.0** | +ext+2_full+2_half measured | xfail |
| 16 | 1111.2 | 1066.3 | **+44.9** | +all measured | xfail |

## Case mismatch classification
- **Cluster A — tiny Δ (<1.5 kWh) (cases 3, 4, 9, 10, 11)**: extended frost mode ON (`2_ext` 측정), `2_full`/`2_half` 미측정. Formula 50이 일부 bin에서 발동. Δ는 0.3 ~ 0.7 kWh 범위로 HSPF 3rd decimal 한 단계 차이.
- **Cluster B — small negative Δ (cases 13, 14)**: `2_half` 측정 / `2_full` 미측정. 동일 fixture를 두 번 등록한 case 13/14는 동일 결과. Δ = -1.5.
- **Cluster C — large positive Δ (cases 12, 15, 16)**: `2_full` 측정. Δ = +32.8 ~ +44.9. Reference expected HSEC가 case 3과 같다 (1079.0) 는 점이 두드러진다.
- **Cluster D — non-extended -7 measured anomaly (case 8)**: extended 없음, `-7_full`/`-7_half`/`-7_ext` 모두 측정. Reference expected는 case 6 (only -7_full 측정) 과 정확히 같다 (1077.2). Repo는 -7_full과 -7_half 양쪽을 모두 사용해 중간 값 (1078.5) 을 산출.

Reference script가 case 12/15에서 `2_full` 측정값을 frost half/full 양쪽에 강제 주입해 P_j가 크게 변동될 가능성 (091 메모) 은 **반대로 뒤집힌다**: reference expected HSEC는 case 3 (1079.0) 과 동일하므로, reference는 `2_full` 측정값을 frost full 곡선에 **반영하지 않는** 쪽으로 해석한 것으로 보인다 (즉 frost 2_full 측정도 무시하고 default 보간점 사용). 091의 가설은 본 audit으로 갱신 필요.

## Per-bin / branch findings
tj=-1, 0, 2, 5 frost bin에서 case 3 vs case 12/15/16 actual bin trace:

case 3 (default 2_full_f):
- tj=-1 formula50 P_j ≈ 1512.5
- tj=0  formula49 P_j ≈ 1201.2
- tj=2  formula49 P_j ≈ 858.4
- tj=5  formula49 P_j ≈ 534.4

case 12 (2_full 측정 → 2_full_f = 2800):
- tj=-1 formula50 P_j ≈ 1543.6  (+31)
- tj=0  formula50 P_j ≈ 1300.6  (+99, branch가 49→50으로 바뀜)
- tj=2  formula50 P_j ≈ 944.0   (+86, branch가 49→50으로 바뀜)
- tj=5  formula49 P_j ≈ 555.0

case 16 (모든 측정):
- tj=-1 saturated P_j = 1566.7  (load > ext capacity → backup heat 동반)
- tj=0  formula50 P_j = 1514.2
- tj=2  formula50 P_j = 1005.2
- tj=5  formula49 P_j = 553.8

처음 갈라지는 지점:
- Cluster C: 측정 2_full로 인해 `2_full_f` 가 default (3621.4) → 2800 으로 낮아지고, frost full capacity curve의 slope가 변해 **branch selection이 49→50** 으로 옮겨가는 bin이 늘어난다. P_j 자체도 frost cop_full(tg)이 다른 값으로 평가되어 함께 증가.
- Cluster A: 같은 frost full 곡선은 default 그대로지만, extended frost curve (`_iso_hspf_extended_frost_curve`) 가 활성화되어 tj=-1 bin이 formula49 → formula50으로 빠지는 효과 + tg/tf 계산식 차이가 0.3 kWh 수준의 Δ를 만든다.
- Cluster D (case 8): saturated branch에서 -7_full+-7_half 측정이 모두 frost half/full 곡선의 -7 endpoint로 반영되어 ext가 없는데도 half line이 변해 Δ를 만든다. Reference는 -7_half 측정을 무시한 듯.

## Extended endpoint findings
- `_iso_hspf_has_extended_candidate(resolved)` → `2_ext` 존재 여부만 본다. 다른 ext key는 활성화 조건이 아님.
- `_iso_hspf_has_frost_extended_candidate(resolved)` → `2_ext` 있거나 (`-7_ext` AND `2_ext_f`) 있으면 True. official case 모두 `2_ext` 입력으로 활성화된다.
- `_iso_hspf_has_non_frost_extended_candidate(resolved)` → `7_ext` AND `-7_ext` 둘 다 필요. official case에는 `7_ext` 없음 → Formula 47 비활성. **남은 mismatch는 전부 frost 경로 안의 문제**임을 보장.
- `_iso_hspf_extended_minus7_default()`: `-7_ext` 측정 있으면 그대로, 없으면 `2_ext × 0.734/0.877` 기본값. 0.734/0.877의 출처는 코드 내 주석 없음. → **원문 확인 필요 항목**.
- `_iso_hspf_extended_frost_curve()` / `_iso_hspf_common_extended_frost_curve()`: -7°C ↔ 2°C 사이 1차 보간. 2°C endpoint는 `2_ext_f` 우선, 없으면 `2_ext`. Cluster A의 0.3 kWh Δ는 이 보간 결과의 endpoint 선택 (특히 `-7_ext` default factor) 가능성이 가장 높다.
- `_iso_hspf_resolve_common_points()`: 측정 `2_{stage}` 입력은 `2_{stage}_f` (frost용) 키에만 보존되며 `2_{stage}` 키는 `-7→7` 라인 위 계산점으로 덮어쓴다. reference는 측정 2_full을 frost 곡선에 사용하지 않는 듯하므로, repo와 reference의 frost 2-point 해석이 달라진다.

## Original-text audit needed
- ISO 16358-2 원문에서 다음 사항을 확인해야 한다 (audit 이후 결정):
  1. **`2_{stage}_f` 측정의 frost 곡선 반영 여부.** 측정 `2_{stage}`가 입력되었을 때 frost 곡선 (-7°C ↔ 2°C 보간) 의 2°C endpoint로 사용되어야 하는지, 아니면 항상 비frost (-7°C ↔ 7°C) 라인 위의 계산점만 써야 하는지.
  2. **`-7_ext` default factor 0.734 / 0.877의 출처.** 표준에 명시된 값인지, 외부 reference script의 휴리스틱인지.
  3. **`-7_full` / `-7_half` 측정의 동시 적용 규칙.** reference가 case 8에서 -7_half 측정을 무시한 듯한 거동이 원문 기준에 맞는지.
  4. **Formula 50 적용 범위.** half < bl_h ≤ full < bl_h ≤ ext 의 정확한 절단 조건이 capacity 라인 기준인지 (현재 구현) 또는 다른 형태인지.
  5. **Saturated/backup heat 처리.** `bl_h > snapshot["ext"]["capacity"]` 일 때 auxiliary가 어떤 단위 (W, COP=1) 로 더해지는지.
- bin_hours, HSTL, 2_full → 2_full_f 매핑은 이미 091/096/097/098에서 확인됨 → 반복 audit하지 않음.

## Recommended next targeted patch (audit 통과 후)
원문 audit 결과 다음 중 하나가 정해지면 minimal targeted patch가 가능하다.

후보 1 — frost 2-point endpoint 정책 변경 (Cluster C, B 해소 가능):
- `_iso_hspf_capacity_curve` / `_iso_hspf_power_curve`의 frost branch에서 `2_{stage}_f` 우선 참조를 제거하고 항상 `2_{stage}` (계산점) 만 사용한다.
- 측정 2_full / 2_half는 그러면 frost 곡선에 반영되지 않으므로 case 12/13/14/15/16이 reference에 수렴할 가능성 큼.
- 단, 091의 reference-overwrite 가설이 부분적으로 옳을 가능성도 있으므로 원문 확인 필요.

후보 2 — `-7_ext` default factor 정정 (Cluster A 해소 가능):
- 0.734 / 0.877 → 원문 표 기반 값으로 교체.
- Cluster A의 0.3 kWh Δ를 줄일 수 있음.

후보 3 — saturated branch에서 -7_{stage} measured 적용 정책 (Cluster D, case 8):
- reference가 `-7_full` 우선, `-7_half` 무시인지, 또는 stage별 우선순위가 있는지 원문 확인.

원문 audit이 끝날 때까지 위 patch들은 모두 **보류**한다. 검증을 위한 별도 focused test는 patch와 함께 작성한다.

## Explicit no-change list
- `core/calculator_iso16358.py` 의 모든 계산식.
- `tests/fixtures/iso16358_hspf_official_exact_cases.json` 의 expected / point_pool / cases.
- `tests/test_iso16358_hspf_official_exact_golden.py` 의 `XFAIL_CASE_IDS`.
- branch / case naming, trace schema.
- ISO table Excel-like UI, AHRI/EN/UI, adapter, ML.
- result report active/archive/summaries 이동.
- 본 audit은 report와 WORK_PLAN만 수정한다.

## task 5 — WORK_PLAN
- 다음 작업은 **원문 audit** 으로 둔다. 위 5개 항목을 사용자가 ISO 16358-2 원문에서 확인하면, 그 결과에 따라 targeted patch (후보 1/2/3) 를 별도 작업으로 분리해 진행.
- ISO table Excel-like behavior patch 등 UI 작업은 HSPF mismatch 흐름이 끝날 때까지 뒤로 미룬다.
- lifecycle maintenance는 이번 audit 범위가 아니므로 수행하지 않는다 (audit 결과를 record 하기 위한 report 한 개만 active에 추가).

## Verification
- `python3 -B -m py_compile core/calculator_iso16358.py` → OK
- `python3 -B -m pytest tests/test_iso16358_hspf_frost_trace.py -q` → 8 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_boundary_cop_alignment.py -q` → 6 passed, 1 skipped
- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py -q` → all pass
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q` → all pass
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` → 6 passed, 11 xfailed (변화 없음)
- `python3 -B -m pytest -q` → 411 passed, 4 skipped, 34 xfailed (변화 없음)

## Known Risks
- 원문 audit 결과에 따라 위 후보 1/2/3 중 어떤 것이 적용 가능한지 결정될 때까지 mismatch는 그대로 유지된다.
- result report lifecycle maintenance pending: active 폴더가 098까지 누적되어 archive 정리가 필요하지만 본 audit 범위에서는 수행하지 않음.

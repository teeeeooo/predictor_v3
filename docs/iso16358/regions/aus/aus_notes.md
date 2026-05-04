# AS/NZS 3823.4 Regional Notes

## 1. Overview

| Item | Value |
|------|-------|
| 규격 | AS/NZS 3823.4 |
| 대상 지역 | Australia / New Zealand |
| Climate 종류 | Hot & Humid / Mixed / Cold |
| 구현 상태 | 문서화 완료, 구현 대기 중 |
| 구현 금지 조건 | AS/NZS 3823.4.2 원문 확인 전 임의 구현 금지 |
| 문서 성격 | Regional research memo, not implementation spec |

---

## 2. Seasonal Performance Metrics

| Symbol | Formula | 대기전력 포함 | 공식 출력 여부 |
|--------|---------|-------------|--------------|
| FCSP | LCST / CCSE | 미포함 | 공식 출력 |
| FTCSP | LCST / Total_cooling_energy | 포함 | 구현하되 출력 안 함 |
| FHSP | LHST / CHSE | 미포함 | 참고값 출력 |
| FTHSP | LHST / Total_heating_energy | 포함 | 공식 출력 |

---

## 3. Standby Power Calculation

| Item | Value |
|------|-------|
| 입력 | P_inactive (W) — 사용자 실측 입력, 냉난방 공통 단일값 |
| 난방 계수 | 0.4 (규격 고정값) |
| 냉방 계수 | 0.6 (규격 고정값) |

수식:
- Standby_heating = P_inactive × Inactive_heating_hours × 0.4
- Standby_cooling = P_inactive × Inactive_cooling_hours × 0.6
- Total_heating_energy = CHSE + Standby_heating
- Total_cooling_energy = CCSE + Standby_cooling

주의: 대기전력은 Inactive hours에만 곱한다. Active hours에는 적용하지 않는다.

---

## 4. Season Hours by Climate

### 4.1 Hot & Humid

| Season | Active | Inactive | Disconnected | Total |
|--------|--------|----------|--------------|-------|
| Cooling | 2247 | 6236 | 277 | 8760 |
| Heating | 277 | 6236 | 2247 | 8760 |

### 4.2 Mixed

| Season | Active | Inactive | Disconnected | Total |
|--------|--------|----------|--------------|-------|
| Cooling | 840 | 6629 | 1291 | 8760 |
| Heating | 1291 | 6629 | 840 | 8760 |

### 4.3 Cold

| Season | Active | Inactive | Disconnected | Total |
|--------|--------|----------|--------------|-------|
| Cooling | 545 | 5555 | 2660 | 8760 |
| Heating | 2660 | 5555 | 545 | 8760 |

참고: ISO 16358 default (냉방 Active 1817 / 난방 Active 2866)와 다르다.
      AS/NZS는 climate별로 별도 시간 구조를 사용한다.

---

## 5. Bin Hours by Climate

### 5.1 Hot & Humid — Cooling Bin

| t_0 | t_100 | 비고 |
|-----|-------|------|
| 21°C | 33°C | T1 load 0% / 100% |

| tj (°C) | nj (h) |
|---------|--------|
| 22 | 51 |
| 23 | 98 |
| 24 | 153 |
| 25 | 198 |
| 26 | 255 |
| 27 | 256 |
| 28 | 253 |
| 29 | 260 |
| 30 | 223 |
| 31 | 165 |
| 32 | 112 |
| 33 | 102 |
| 34 | 59 |
| 35 | 30 |
| 36 | 16 |
| 37 | 12 |
| 38 | 4 |
| Total | 2247 |

### 5.2 Hot & Humid — Heating Bin

| t_0_heat | t_100_heat | 비고 |
|----------|-----------|------|
| 15°C | 0°C | H1 load 0% / 82% |

| tj (°C) | nj (h) |
|---------|--------|
| 3 | 1 |
| 4 | 4 |
| 5 | 10 |
| 6 | 17 |
| 7 | 29 |
| 8 | 30 |
| 9 | 53 |
| 10 | 43 |
| 11 | 30 |
| 12 | 26 |
| 13 | 19 |
| 14 | 15 |
| Total | 277 |

### 5.3 Mixed — Cooling Bin

| t_0 | t_100 |
|-----|-------|
| 21°C | 33°C |

| tj (°C) | nj (h) |
|---------|--------|
| 22 | 36 |
| 23 | 58 |
| 24 | 67 |
| 25 | 83 |
| 26 | 76 |
| 27 | 88 |
| 28 | 80 |
| 29 | 78 |
| 30 | 50 |
| 31 | 56 |
| 32 | 42 |
| 33 | 25 |
| 34 | 22 |
| 35 | 19 |
| 36 | 18 |
| 37 | 17 |
| 38 | 13 |
| 39 | 3 |
| 40 | 3 |
| 41 | 3 |
| 42 | 2 |
| 43 | 1 |
| Total | 840 |

### 5.4 Mixed — Heating Bin

| t_0_heat | t_100_heat |
|----------|-----------|
| 15°C | 0°C |

| tj (°C) | nj (h) |
|---------|--------|
| -4 | 1 |
| -3 | 1 |
| -2 | 4 |
| -1 | 9 |
| 0 | 23 |
| 1 | 37 |
| 2 | 47 |
| 3 | 64 |
| 4 | 108 |
| 5 | 99 |
| 6 | 132 |
| 7 | 128 |
| 8 | 122 |
| 9 | 143 |
| 10 | 112 |
| 11 | 103 |
| 12 | 79 |
| 13 | 53 |
| 14 | 26 |
| Total | 1291 |

### 5.5 Cold — Cooling Bin

| t_0 | t_100 |
|-----|-------|
| 21°C | 33°C |

| tj (°C) | nj (h) |
|---------|--------|
| 22 | 16 |
| 23 | 29 |
| 24 | 40 |
| 25 | 48 |
| 26 | 50 |
| 27 | 52 |
| 28 | 44 |
| 29 | 68 |
| 30 | 48 |
| 31 | 54 |
| 32 | 40 |
| 33 | 25 |
| 34 | 12 |
| 35 | 8 |
| 36 | 6 |
| 37 | 2 |
| 38 | 3 |
| Total | 545 |

### 5.6 Cold — Heating Bin

| t_0_heat | t_100_heat |
|----------|-----------|
| 15°C | 0°C |

| tj (°C) | nj (h) |
|---------|--------|
| -6 | 3 |
| -5 | 13 |
| -4 | 22 |
| -3 | 44 |
| -2 | 54 |
| -1 | 69 |
| 0 | 77 |
| 1 | 116 |
| 2 | 121 |
| 3 | 156 |
| 4 | 169 |
| 5 | 216 |
| 6 | 238 |
| 7 | 327 |
| 8 | 262 |
| 9 | 245 |
| 10 | 189 |
| 11 | 163 |
| 12 | 101 |
| 13 | 52 |
| 14 | 23 |
| Total | 2660 |

---

## 6. Region Config Schema (미확정 항목 포함)

아래는 구현 시 사용할 JSON config 스키마 초안이다.
AS/NZS 3823.4.2 원문 확인 전까지 실제 JSON 파일을 생성하지 않는다.

```json
{
  "_comment": "AS/NZS 3823.4 — [climate] climate config. 구현 대기 중.",
  "climate": "hot_humid | mixed | cold",
  "standby": {
    "heating_factor": 0.4,
    "cooling_factor": 0.6,
    "inactive_heating_hours": 6236,
    "inactive_cooling_hours": 6236
  },
  "season_hours": {
    "cooling": { "active": 2247, "inactive": 6236, "disconnected": 277 },
    "heating": { "active": 277, "inactive": 6236, "disconnected": 2247 }
  },
  "hspf": {
    "load_line": {
      "source": "rated_heating_capacity",
      "zero_load_temp": 15,
      "full_load_temp": 0,
      "rated_capacity_factor": 0.82
    },
    "frost_boundaries": {
      "lower": "미확정 — AS/NZS 원문 확인 필요",
      "upper": "미확정 — AS/NZS 원문 확인 필요"
    }
  },
  "cspf": {
    "t_0_load": 21,
    "t_100_load": 33,
    "Cd": "미확정 — AS/NZS 원문 확인 필요"
  },
  "bin_hours": [],
  "hspf_bin_hours": []
}
```

---

## 7. 미확정 항목

| 항목 | 상태 | 비고 |
|------|------|------|
| frost 경계 온도 | 미확정 | AS/NZS 3823.4.2 원문 확인 필요 |
| Cd (냉방 degradation) | 미확정 | AS/NZS 원문 확인 필요 |
| Cd (난방 degradation) | 미확정 | AS/NZS 원문 확인 필요 |
| load line capacity source | 잠정 tentative_rated_heating_capacity | 원문 확인 후 확정 |
| -7°C 외삽 계수 | 잠정 ISO 16358-2 동일 | 원문 확인 후 확정 |
| 2°C 각주 d 수식 적용 여부 | 미확정 | AS/NZS 원문 확인 필요 |
| FTCSP 공식 출력 여부 | 미출력 확정 | 구현은 하되 UI 노출 안 함 |

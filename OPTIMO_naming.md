# OPTIMO — 프로그램 네이밍 정리

## 전체 프로그램
**OPTIMO** (옵티모)
- 의미: Optimize + Maximum
- "최적 성능/사양을 찾아주는 엔진"
- 사용 예: "옵티모 돌려봤어?"

---

## 하위 모듈

| 모듈 | 기능 | 이름 |
|---|---|---|
| 예측 | HW 사양 입력 → 소비전력 / 효율 예측 출력 | **WATT-son** |
| 역탐색 | 목표 효율 입력 → 최적 HW 조합 출력 | **AeroMatch** |
| 계산기 | 성능 측정값 입력 → 지역별 규격 효율 계산 출력 | **G.R.A.D.E.** (후보) / **Calculator** (후보) |

---

## 모듈별 의미

### WATT-son
- Watt(소비전력) + Watson(명탐정의 조수)
- HW 사양에서 소비전력과 효율을 정밀하게 추리해내는 조력자

### AeroMatch
- Aero(Air-to-Air 공조) + Match(매칭/탐색)
- 목표 효율을 달성할 최적 HW 조합을 역방향으로 찾아줌

### G.R.A.D.E.
- **G**lobal **R**ating **A**nd **D**iagnostic **E**ngine
- 지역별 글로벌 규격(CSPF, SEER2, HSPF2 등)에 따라 효율을 계산하고 판정

---

## 구조 요약

```
OPTIMO
├── WATT-son   : HW 사양 → 소비전력 예측
├── AeroMatch  : 목표 효율 → HW 역탐색
└── G.R.A.D.E. : 측정값 → 글로벌 규격 효율 계산
```

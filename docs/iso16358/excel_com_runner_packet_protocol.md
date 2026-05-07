# Excel COM Runner Packet Protocol

## 1. Purpose

Windows Excel COM runner는 AS/NZS / Energy Rating SEER calculator 원본 workbook의 신뢰 기준값을 추출하기 위한 도구다.

Codespaces, iMac, Numbers, xlsx 변환본에서 관찰한 값은 reference source로 쓰지 않는다. 이러한 값은 converted workbook 또는 old observation diagnostic artifact로만 취급한다.

회사 PC 밖으로 상세 파일을 반출할 수 없으므로 runner는 상세 결과를 회사 PC 로컬에 `full_dump`로 저장하고, 외부 ChatGPT에는 20줄 이하 `chat_packet`만 수동 전달하는 방식을 표준으로 사용한다.

## 2. Roles

| Role | Responsibility |
| --- | --- |
| ChatGPT | case input packet 작성, 결과 해석, 다음 slice 설계 |
| Company PC Excel COM runner | 원본 Excel 계산, full_dump 저장, chat_packet 생성 |
| Codex | repo 코드 수정, 테스트 실행, diff 확인 |
| User | 회사 PC에서 runner 실행, chat_packet만 수동 전달 |

## 3. Runner Output Policy

| Output | Scope | Policy |
| --- | --- | --- |
| `full_dump` | 회사 PC 로컬 보관용 상세 csv/txt | component table, branch cells, baseline cells, intermediate diagnostics를 포함할 수 있다. 외부로 반출하지 않는다. |
| `chat_packet` | 외부 ChatGPT 전달용 요약 | 20줄 이하로 제한한다. 상세 component table 전체를 넣지 않는다. |

`chat_packet`에는 필요한 경우 top mismatch bins, baseline, branch flags, next hint만 넣는다. 상세 표를 손으로 옮기지 말고 runner summary를 조정해 필요한 요약만 출력한다.

## 4. Standard Chat Packet Format

```text
CASE_ID=case3
REFERENCE=Windows Excel COM original workbook
BRANCH_SELECTOR=K25=YES,K26=YES
BASELINE=H12:1126.120,H13:4.33824,CH48_Wh:1126120.47
COMMON=HSEC_Wh:1134087.84,HSPF:4.308
DELTA=+7967.37Wh

TOP_MISMATCH_BINS:
1) tj=..., common_P=..., excel_component=..., diff_hint=...
2) tj=..., common_P=..., excel_component=..., diff_hint=...
3) tj=..., common_P=..., excel_component=..., diff_hint=...

ROUTING_FLAGS:
CB23_ZERO_REASON=...
BO28_ZERO_REASON=...
FORMULA49_ALL_1_5_REJECT=YES/NO/UNKNOWN
LIKELY_CAUSE=...
NEXT_HINT=...
```

## 5. Standard Input Packet Format

ChatGPT가 runner에 전달할 input packet은 아래 형식을 기본으로 사용한다.

```text
CASE_ID=case3
SHEET=Inverter AC
SET_CELLS:
K25=YES
K26=YES
G41=4300
H41=1320
G42=2300
H42=450
G43=680
H43=150
G44=4200
H44=1700

READ_BASELINE:
H12
H13
CH48

READ_ROWS:
21:30

READ_COMPONENT_COLUMNS:
BM,BO,BQ,BS,BT,BU,BX,BZ,CB,CD,CE,CF,CG,CH

CHAT_PACKET_MAX_LINES=20
```

## 6. Runner Template Pseudocode

실제 runner 파일은 repo에 추가하지 않는다. 회사 PC의 로컬 runner는 아래 흐름을 따른다.

```text
load input_packet
open workbook with Windows Excel COM
select SHEET

for each SET_CELLS entry:
    write value to workbook cell

calculate workbook

read READ_BASELINE cells
read READ_ROWS x READ_COMPONENT_COLUMNS into local detail rows
write full_dump locally as csv/txt

if common reference values are provided:
    compute current-vs-Excel deltas
    select top mismatch bins
    infer branch/routing flags when available

build chat_packet with:
    case id
    reference source
    branch selectors
    baseline
    common comparison if provided
    top mismatch bins
    routing flags
    next hint

print chat_packet only
```

## 7. Important Cautions

- Excel COM result from the original Windows workbook is the trusted reference.
- Converted workbook and Numbers observations are diagnostic artifacts only.
- Do not wire an Excel compatibility helper into the production common ISO path without an explicit design decision.
- Do not manually transcribe large tables. Adjust the runner to summarize instead.
- Keep `chat_packet` short enough to move by hand without introducing transcription errors.

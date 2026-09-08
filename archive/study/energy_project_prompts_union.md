# Antigravity CLI — Energy Consumption AI Assistant

통합 Step-by-Step Development Prompts

---

## 0. 이 문서의 목적

이 문서는 두 개의 기존 프롬프트 문서를 단순히 이어 붙인 것이 아니다.

두 문서의 역할을 비교하여 다음 원칙으로 하나의 일관된 개발 프롬프트 세트로 재구성했다.

- **Step의 큰 순서와 핵심 개발 단계는 `01_prompts_energy.md`를 기준으로 한다.**
- **에너지 데이터의 실제 의미, 30분 → 일별 데이터 → 분석 Summary → Context Injection → 필요 시 Tool 조회라는 데이터 흐름은 `antigravity_energy_project_prompts.md`의 설계를 기준으로 한다.**
- 두 문서에 중복되는 내용은 하나로 통합한다.
- 한 문서에만 있던 중요한 요구사항은 해당 Step에 흡수한다.
- 데이터 분석은 단순 total/average/max/min을 넘어 AI가 실제 질문에 답할 수 있도록 설계한다.
- Summary와 원본 데이터 조회의 책임을 명확히 분리한다.
- 특정 날짜/기간처럼 Summary에 없는 정보는 LLM이 추측하지 않고, 이후 Function Calling을 통해 실제 Firestore 데이터를 조회할 수 있도록 설계한다.
- 각 Step에서 미래 기능을 미리 구현하지 않는다.
- 각 Step은 Antigravity CLI에 하나씩 전달하고, 코드/실행/테스트를 확인한 뒤 다음 Step으로 이동한다.

---

# 1. Project Data Context

## Raw Energy Dataset

원본 데이터는 30분 단위 개인 전력 사용량 데이터이다.

주요 컬럼:

```text
Consumption (kwh)
Estimated Cost Inc. Tax (p)
Standing Charge Inc. Tax (p)
Start
End
```

데이터 기간:

```text
2026-03-01 ~ 2026-08-31
```

### 핵심 데이터 의미

- `Consumption (kwh)`는 해당 30분 구간에서 실제로 사용한 에너지량이다.
- 따라서 하루 사용량은 같은 local calendar date에 속하는 모든 30분 단위 `Consumption (kwh)`를 **합산**한다.
- 이미 kWh 단위의 구간 사용량이므로 30분 값에 다시 `0.5`를 곱하지 않는다.
- 애플리케이션의 주요 시계열 데이터 단위는 **daily electricity consumption (kWh/day)** 이다.
- 원본 30분 데이터는 가능한 한 보존한다.
- 별도의 preprocessing 결과로 daily dataset을 생성한다.
- `Start`와 `End`의 timezone 정보를 존중한다.
- 날짜 추출을 위해 UTC로 무조건 변환하여 local date가 바뀌는 오류를 만들지 않는다.
- `Estimated Cost Inc. Tax (p)`는 estimated cost이므로 실제 청구 금액과 동일하다고 단정하지 않는다.
- 비용을 분석할 경우 단위(pence/pounds)를 명확히 표시한다.

---

# 2. 최종 데이터 흐름

이 프로젝트의 핵심 데이터 흐름은 다음과 같다.

```text
Raw Energy Data
30-minute readings
        │
        ▼
Data Validation
        │
        ▼
Preprocessing
30-minute → local calendar date
        │
        ▼
Daily Energy Data
date + daily_consumption_kwh
        │
        ├──────────────────────────────┐
        │                              │
        ▼                              ▼
Firestore                      Analysis / Summary Service
        │                              │
        │                              ▼
        │                       Energy Summary JSON
        │                              │
        │                              ▼
        │                       Context Injection
        │                              │
        │                              ▼
        │                             GPT
        │                              │
        │                 ┌────────────┴────────────┐
        │                 │                         │
        │          Summary sufficient?        Need raw/detail?
        │                 │                         │
        │                YES                        NO
        │                 │                         │
        │                 ▼                         ▼
        │              Answer                Function Calling
        │                                           │
        │                                           ▼
        └──────────────────────────────────── Firestore
                                                    │
                                                    ▼
                                               Tool Result
                                                    │
                                                    ▼
                                                   GPT
                                                    │
                                                    ▼
                                                  Answer
```

### 핵심 원칙

**모든 원본 데이터를 GPT에게 전달하지 않는다.**

먼저 데이터를 분석하여 AI가 자주 필요로 하는 의미 있는 정보를 Summary로 만든다.

예:

- 전체 평균
- 전체 기간
- 최대/최소 및 날짜
- 월별 통계
- 평일/주말 비교
- 요일별 패턴
- 최근 7일/30일
- 추세
- 비용 통계

반면 Summary에 없는 특정 날짜의 값은 GPT가 추측하지 않는다.

예:

```text
"What was my consumption on 2026-08-13?"
```

이 질문은 나중에 내부 data query tool을 통해 실제 Firestore 데이터를 조회한다.

---

# 3. Development Rules

모든 Step에 다음 규칙을 적용한다.

1. 각 Step을 한 번에 하나씩 Antigravity CLI에 전달한다.
2. 현재 Step의 결과를 직접 확인한 뒤 다음 Step으로 넘어간다.
3. `mission_statement.txt`가 저장소에 있다면 반드시 처음부터 끝까지 읽고 authoritative specification으로 사용한다.
4. mission에 없는 내용을 필수 요구사항으로 임의 추가하지 않는다.
5. 현재 Step에서 요청하지 않은 미래 기능을 미리 구현하지 않는다.
6. 기존 코드를 수정할 때는 현재 기능을 불필요하게 깨뜨리지 않는다.
7. 실제 데이터가 존재하는 경우 예시값을 만들어내지 말고 실제 데이터를 검사한다.
8. 데이터 이상을 발견하면 조용히 수정하지 말고 보고한다.
9. API key, Firebase credentials 등의 secret을 코드에 하드코딩하지 않는다.
10. 데이터 분석 결과는 재사용 가능한 service/function으로 만든다.
11. Router에는 business logic을 과도하게 넣지 않는다.
12. Summary에 없는 정보를 LLM이 추측하지 못하도록 prompt를 설계한다.
13. 모든 단계 완료 후에는 무엇을 구현했고 무엇이 남았는지 명확히 보고한다.
14. 마지막에는 실제 구현 상태를 코드와 테스트 근거로 감사한다.

---

# STEP 1 — Project Setup + Architecture

## Prompt

```text
You are helping me build an educational AI Native project step by step.

First, read the entire mission_statement.txt in this repository and treat it as the authoritative specification. (Do not read any files in archive)

The project is an AI assistant based on personal electricity-consumption data.

DATA CONTEXT:

- Raw data is measured every 30 minutes.
- Data period: 2026-03-01 through 2026-08-31.
- Main raw columns:
  - consumption_kwh
  - estimated_cost_pence
  - standing_charge_pence
  - start
  - end

IMPORTANT DATA SEMANTICS:

- Consumption (kwh) is already the energy consumed during the 30-minute interval.
- Daily electricity consumption must therefore be calculated by SUMMING all interval Consumption (kwh) values belonging to the same local calendar date.
- Do NOT multiply the interval consumption by 0.5 again.
- Preserve timezone-aware timestamps when determining the local calendar date.
- The application's primary time-series unit is daily electricity consumption in kWh/day.
- Preserve the raw 30-minute data whenever possible.
- Estimated cost must not be described as confirmed actual billing.

The final architecture should conceptually support:

Raw 30-minute data
→ validation
→ daily preprocessing
→ daily energy data
→ Firestore
→ analysis/summary service
→ summary JSON
→ OpenAI context injection
→ GPT
→ if summary is insufficient, later Function Calling
→ Firestore query
→ tool result
→ GPT
→ final answer

For STEP 1 ONLY:

1. Read mission_statement.txt completely.
2. Inspect the current project directory.
3. Summarize the mission requirements.
4. Separate required features from optional bonus features.
5. Design a clean project structure for:
   - backend
   - frontend
   - data
   - tests
   - configuration
6. Create the basic FastAPI application.
7. Create requirements.txt with appropriate packages for the current project stage.
8. Create .gitignore.
9. Create .env.example with future environment variables, without real secrets.
10. Configure basic CORS structure.
11. Create placeholder folders/files for:
    - routers
    - services
    - models
    - database
    - analysis
    - tests
12. Create GET /health.
13. Make sure the FastAPI app can run locally.
14. Document the planned end-to-end architecture without implementing future functionality.

The architecture must preserve a clear separation between:

- raw data
- preprocessing
- daily data
- analysis/summary
- database
- API
- AI/chat
- frontend

DO NOT implement:
- Firestore CRUD
- OpenAI
- chat
- conversation history
- actual energy-data analysis
- Function Calling
- MCP
- frontend
- deployment

After completing STEP 1:

1. Explain the purpose of each important file.
2. Explain the planned data flow.
3. Explain how to run FastAPI locally.
4. Stop and wait.
```

### Step 1 확인 포인트

- 프로젝트 구조가 이후 단계와 자연스럽게 연결되는가?
- raw data / daily data / analysis / API / AI가 분리되어 있는가?
- 아직 미래 기능을 구현하지 않았는가?
- mission의 required/bonus가 구분되어 있는가?

---

# STEP 2 — Energy Data Preparation + Analysis / Summary

## Prompt

```text
Continue the project from STEP 1.

IMPORTANT:
Only implement STEP 2. Do not implement later application features.

This is the most important data-engineering and analysis step.

First inspect the actual energy dataset file in the data/raw/ folder. Do not assume its filename.

DATA CONTEXT:

- Period: 2026-03-01 through 2026-08-31.
- Raw interval: 30 minutes.
- Columns:
  - consumption_kwh
  - estimated_cost_pence
  - standing_charge_pence
  - start
  - end

IMPORTANT DATA SEMANTICS:

- Consumption (kwh) is already the energy consumed in that 30-minute interval.
- Daily consumption = SUM of all interval Consumption (kwh) values belonging to the same local calendar date.
- Do NOT multiply Consumption by 0.5 again.
- Respect the timestamp timezone when extracting the local date.
- Do not silently shift dates by converting everything to UTC first.
- Preserve the raw data.
- Estimated cost is not necessarily an actual bill.

PART A — Raw Data Validation

Inspect and report:

1. Actual filename and location.
2. Number of raw rows.
3. Actual columns.
4. Data types.
5. Minimum and maximum timestamps.
6. Missing values.
7. Duplicate records.
8. Invalid numeric values.
9. Invalid timestamps.
10. Invalid Start/End relationships.
11. Whether intervals are approximately 30 minutes.
12. Whether normal days contain approximately 48 records.
13. Missing dates.
14. Missing intervals.
15. Unexpected gaps.
16. Suspicious anomalies.
17. Whether the actual data period matches the expected period.

Do not silently repair suspicious data.

If the data has DST/timezone-related behavior or any other legitimate reason for a day not to have exactly 48 records, explain it rather than blindly labeling it as an error.

PART B — Daily Preprocessing

Create a reusable preprocessing workflow:

30-minute raw data
→ timezone-aware local date
→ group by local date
→ SUM Consumption (kwh)
→ daily dataset

The minimum daily fields are:

- date
- daily_consumption_kwh

If cost fields can be meaningfully aggregated (just sum of 48 records for each date):

- calculate them separately
- document their units
- document what they represent
- never describe estimated cost as confirmed billing

Do not modify the raw dataset.

Create a reproducible preprocessing function/module and a validation test or script.

PART C — Energy Analysis Summary

Create a reusable analysis/summary service that accepts the daily dataset and returns structured Python data suitable for JSON serialization.

Do NOT stop at total/average/max/min.

The summary must support the kinds of questions an electricity-consumption assistant is expected to answer.

Include:

1. PERIOD
   - start_date
   - end_date
   - analysis period description

2. DATASET COUNTS
   - number of daily records
   - number of raw interval records if useful
   - coverage information
   - missing-date information if relevant

3. OVERALL STATISTICS
   - total consumption
   - average daily consumption
   - minimum daily consumption + date
   - maximum daily consumption + date

4. MONTHLY STATISTICS
   For each month:
   - total consumption
   - average daily consumption
   - number of days

   Also identify:
   - highest-total-consumption month
   - highest-average-consumption month
   - lowest relevant month metric

5. WEEKDAY VS WEEKEND
   - weekday average
   - weekend average
   - absolute difference
   - percentage difference where meaningful

6. DAY-OF-WEEK PATTERNS
   Calculate average consumption for:
   - Monday
   - Tuesday
   - Wednesday
   - Thursday
   - Friday
   - Saturday
   - Sunday

   Identify highest and lowest average day-of-week.

7. RECENT PERIODS
   At minimum:
   - recent 7-day total
   - recent 7-day average
   - recent 30-day total
   - recent 30-day average
   - actual number of days used

   Compare recent averages with overall average.

   If fewer than 30 days are available, explicitly report the actual available period.

8. TREND
   Create a transparent trend calculation.

   - Primary: 7-day rolling average → identify short-term trend
   - Secondary: Linear regression slope with daily consumption → quantify overall direction
   - Supporting: Monthly average comparison → explain longer-term changes or comparable recent-vs-earlier period averages

   Do not blindly compare only the first and last individual day.

   Return:
   - increasing / decreasing / stable (but only when the change exceeds a predefined threshold (e.g. ±5%) to avoid calling tiny fluctuations a trend)
   - magnitude such as percentage change
   - periods used
   - calculation method

9. COST STATISTICS
   If cost data is sufficiently reliable:
   - estimated cost totals
   - relevant averages
   - clear unit
   - clear estimated-cost label

10. EXTREMES
   Ensure maximum/minimum values are paired with their dates.

PART D — Summary Design

Use a structured hierarchy similar to:

{
  "period": {...},
  "count": {...},
  "overall": {...},
  "monthly": {...},
  "weekday_weekend": {...},
  "day_of_week": {...},
  "recent": {...},
  "trend": {...},
  "extremes": {...},
  "cost": {...}
}

Exact field names may follow the code style, but preserve the meaning.

IMPORTANT SUMMARY BOUNDARY:

The summary must NOT contain every individual daily record merely to make the LLM capable of answering everything.

For example:

max:
  value: 82.4
  date: 2026-07-21

allows:
"When was my highest-consumption day?"

But if the summary does not contain the value for 2026-08-13, the LLM must not invent it.

Specific-date and arbitrary date-range questions should remain candidates for a future database query / Function Calling tool.

The summary function must be deterministic and must not mutate the input/raw dataset.

Do NOT:
- connect to Firestore
- connect to OpenAI
- implement chat
- build frontend
- implement Function Calling
- deploy

Use pandas where appropriate.

After implementation:

1. Show actual raw-data validation results.
2. Show the exact preprocessing flow.
3. Show actual raw row count.
4. Show actual daily record count.
5. Show missing dates/intervals.
6. Show important anomalies.
7. Show an actual generated summary from the project data.
8. Explain each major summary section.
9. Explain the trend calculation.
10. Give 10–15 questions the summary can answer.
11. Give questions the summary cannot answer.
12. Explain why those questions require additional data retrieval.
13. Tell me exactly which files were created/modified.
14. Stop and wait.
```

### Step 2 확인 포인트

반드시 다음을 직접 확인한다.

```text
30-minute data
      ↓
local calendar date
      ↓
SUM(Consumption)
      ↓
daily_consumption_kwh
      ↓
analysis
      ↓
summary
```

특히:

- `Consumption × 0.5`를 하지 않았는가?
- local timezone 기준으로 날짜를 만들었는가?
- max/min에 date가 같이 있는가?
- monthly / weekday_weekend / day_of_week / recent / trend가 있는가?
- Summary가 모든 daily records를 불필요하게 포함하지 않는가?
- 실제 데이터의 이상치를 숨기지 않았는가?

---

# STEP 3 — FastAPI + Pydantic

## Prompt

```text
Continue the project from STEP 2.

IMPORTANT:
Only implement STEP 3. Do not implement later steps.

Build the FastAPI API structure and Pydantic request/response models.

The application's main data unit is DAILY electricity consumption.

The conceptual mission data model is:

(date, value, memo)

For this project:

- date = local calendar date
- value = daily electricity consumption in kWh
- memo = optional user note

Reuse the analysis/service architecture created in STEP 2.

Create clean separation between:

- routers
- services
- models
- analysis

Prepare Pydantic models for:

- creating daily data
- updating daily data
- returning daily data
- returning summary data
- chat request/response models if the architecture requires placeholders, but do not implement OpenAI yet

Implement these API routes as API structure:

POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}
GET    /api/data/summary

At this stage, do NOT connect to Firestore.

Use temporary in-memory data or a clearly marked temporary repository.

The temporary implementation must still respect:

- daily data
- kWh unit
- date validation
- numeric validation
- memo as optional

Add:

1. Appropriate HTTP status codes.
2. Pydantic validation.
3. Basic error handling.
4. Swagger at /docs.
5. Clear router/service separation.
6. Reuse of the STEP 2 analysis service where appropriate.

Do not implement:

- Firestore
- OpenAI
- chat
- conversation persistence
- frontend
- Function Calling
- MCP
- deployment

After implementation:

1. Explain REST API, CRUD and Pydantic using this energy project.
2. Show the endpoint table.
3. Show one complete request/response example.
4. Explain which implementation is temporary.
5. Explain what STEP 4 will replace.
6. Test endpoints through Swagger or automated API tests.
7. Tell me exactly what changed.
8. Stop and wait.
```

---

# STEP 4 — Firestore + Data CRUD

## Prompt

```text
Continue the project from STEP 3.

IMPORTANT:
Only implement STEP 4. Do not implement later AI/frontend features.

Connect the FastAPI backend to Firebase Firestore.

Use Firebase Admin SDK.

Use environment variables for credentials.

Never hard-code Firebase credentials.

Create/use the Firestore collection:

data

The primary stored application record represents DAILY electricity consumption.

Minimum conceptual structure:

{
  "date": "YYYY-MM-DD",
  "value": <daily consumption in kWh>,
  "memo": "optional note"
}

If the architecture needs additional fields such as:

- consumption_kwh
- estimated_cost_pence
- estimated_cost_pounds
- standing_charge_pence

they may be added only when they have a clear meaning.

Do not duplicate fields unnecessarily.

Implement:

POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}

Replace the temporary repository from STEP 3 with Firestore.

Keep:

router
→ service/repository
→ Firestore

separated.

Handle:

- document not found
- invalid input
- invalid date
- invalid value
- duplicate/consistency concerns where appropriate
- Firestore errors

Keep Pydantic validation.

The application must clearly document that `value` means daily electricity consumption in kWh.

Do not implement:

- OpenAI
- chat
- conversation history
- frontend
- Function Calling
- MCP
- deployment

After implementation:

1. Explain the Firestore document structure.
2. Show one example daily-energy document.
3. Explain POST/GET/PUT/DELETE mapping.
4. Explain credential handling.
5. Test CRUD through Swagger and/or automated tests.
6. Explain what changed from STEP 3.
7. Stop and wait.
```

---

# STEP 5 — Data Summary API

## Prompt

```text
Continue the project from STEP 4.

IMPORTANT:
Only implement STEP 5. Do not implement OpenAI/chat/frontend yet.

Implement:

GET /api/data/summary

The endpoint must use the actual daily electricity-consumption data stored in Firestore.

Flow:

GET /api/data/summary
→ FastAPI router
→ data service/repository
→ Firestore daily data
→ analysis/summary service from STEP 2
→ structured summary JSON
→ response

Do NOT duplicate the analysis logic inside the router.

Reuse the STEP 2 analysis service.

The summary must include, where data permits:

1. period
2. count/coverage
3. total consumption
4. average daily consumption
5. minimum + date
6. maximum + date
7. monthly statistics
8. weekday/weekend statistics
9. day-of-week statistics
10. recent 7-day statistics
11. recent 30-day statistics
12. recent-vs-overall comparison
13. trend
14. estimated cost statistics if reliably available
15. relevant data-quality/coverage information where useful

Important:

- Use actual Firestore data.
- Do not hard-code example values.
- Return clean JSON.
- Use Pydantic response models where appropriate.
- Handle empty datasets.
- Do not include every individual daily record just to enlarge the summary.
- Preserve the distinction between summary information and raw-detail queries.
- Do not implement OpenAI.
- Do not implement Function Calling.
- Do not build frontend.

After implementation:

1. Show an actual response from the project's Firestore data.
2. Explain how each metric is calculated.
3. Explain why max/min dates are included.
4. Explain why monthly, weekday/weekend, day-of-week, recent and trend data are included.
5. Explain why a specific-date question may still require a direct database query.
6. Explain how STEP 6 will consume this summary.
7. Test the endpoint.
8. Stop and wait.
```

---

# STEP 6 — OpenAI Chat + Context Injection

## Prompt

```text
Continue the project from STEP 5.

IMPORTANT:
Only implement STEP 6.

Do not implement conversation persistence, frontend, Function Calling, or MCP yet.

Implement:

POST /api/chat

The flow must be:

User question
→ Chat Router
→ Chat Service
→ Summary Service
→ current Firestore daily data
→ Energy Summary
→ System Prompt + Summary
→ OpenAI API
→ AI response
→ JSON response

Do not put all chat logic inside the router.

Create a dedicated chat service.

The system prompt must establish that the model is an electricity-consumption data assistant.

Inject the actual energy summary generated by the existing summary service.

The injected summary should contain relevant information such as:

- analysis period
- record count/coverage
- total consumption
- average daily consumption
- maximum/minimum + dates
- monthly statistics
- weekday/weekend comparison
- day-of-week patterns
- recent 7-day/30-day statistics
- recent-vs-overall comparison
- trend
- estimated cost information when available

ANTI-HALLUCINATION RULES:

1. Use only information available in the provided summary.
2. Do not invent values, dates, trends or costs.
3. Do not claim a specific day's value unless that value is present in the summary.
4. If the summary does not contain enough information, explicitly say so.
5. Do not fabricate data outside 2026-03-01 through 2026-08-31.
6. Use kWh for energy consumption.
7. Clearly distinguish estimated cost from confirmed billing.
8. Do not imply that a missing value is zero.
9. Do not infer a specific date's value from unrelated aggregate statistics.

Use OPENAI_API_KEY from environment variables.

Keep model/configuration settings configurable.

Never expose the API key to frontend JavaScript.

Add reasonable OpenAI error handling.

Test at least:

1. average daily consumption
2. highest-consumption day
3. weekday vs weekend
4. highest-consumption month
5. recent trend
6. a specific-date question whose value is not in the summary

The last test must verify that the model does NOT invent the answer.

Also test a question outside the dataset period.

After implementation:

1. Show request/response format.
2. Show an example generated system prompt using actual summary data.
3. Explain context injection.
4. Explain why OpenAI credentials remain on the backend.
5. Explain the complete request flow.
6. Show test results.
7. Tell me exactly what was implemented.
8. Stop and wait.
```

---

# STEP 7 — Conversation History

## Prompt

```text
Continue the project from STEP 6.

IMPORTANT:
Only implement STEP 7.
Do not build the frontend, deployment, or Function Calling yet.

Implement conversation history using Firestore.

Collection:

conversations

Implement:

POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}

A conversation should contain at least:

- conversation id
- title/name
- created_at
- updated_at
- messages

Each message should contain:

- role
- content
- timestamp if useful

At minimum support:

- user
- assistant

Modify /api/chat so completed chat exchanges can be automatically persisted according to the mission requirements.

Keep conversation logic in a dedicated conversation service/repository.

Do not mix conversation persistence logic into the data-analysis service.

Ensure:

1. Pydantic validation.
2. Missing conversation ID handling.
3. Complete message history retrieval.
4. Existing energy CRUD continues working.
5. Existing summary continues working.
6. Existing context injection continues working.
7. Credentials remain protected.

Do not implement:

- frontend
- Function Calling
- MCP
- deployment

After implementation:

1. Show Firestore conversation document structure.
2. Explain how a chat becomes a saved conversation.
3. Explain how an old conversation will later be loaded by the frontend.
4. Explain changes to /api/chat.
5. Test save/list/load/delete.
6. Stop and wait.
```

---

# STEP 8 — Frontend

## Prompt

```text
Continue the project from STEP 7.

IMPORTANT:
Only implement STEP 8.
Do not deploy yet.

Build the frontend using ONLY:

- HTML
- CSS
- vanilla JavaScript

Do not use React, Vue, Next.js, or another frontend framework.

Create a clean responsive Electricity Consumption AI Assistant dashboard.

The frontend must consume the existing backend APIs rather than hard-coding data.

UI sections:

1. AI CHAT

- question input
- send button
- conversation display
- loading state
- error state
- clear distinction between user and assistant messages

2. CONVERSATION HISTORY

- previous conversation list
- select conversation
- load complete message history
- display selected conversation

3. DAILY ENERGY DATA MANAGEMENT

Display daily electricity data.

Support:

- list
- add
- edit
- delete

If the mission only requires a subset, implement the required minimum while keeping the architecture ready for full CRUD.

Clearly label:

value = daily electricity consumption (kWh)

4. DATA SUMMARY

Display useful summary information from:

GET /api/data/summary

At minimum show:

- analysis period
- daily record count
- total consumption
- average daily consumption
- maximum + date
- minimum + date
- recent usage
- weekday/weekend comparison
- trend
- useful monthly/day-of-week information where appropriate

5. DATA FLOW UX

The UI should make it understandable that:

raw data
→ daily data
→ analysis
→ summary
→ AI

Do not expose raw API keys.

Keep API communication in a dedicated JavaScript module where practical.

Make API base URL configurable by environment/deployment configuration.

Do not create fake AI responses.

Do not deploy.

After implementation:

1. Show frontend directory structure.
2. Explain each UI section.
3. Explain each fetch/API call.
4. Explain loading/error handling.
5. Explain how conversation history is loaded.
6. Explain how summary data is rendered.
7. Run the frontend and verify major screens.
8. Stop and wait.
```

---

# STEP 9 — Connect & Test Complete Application

## Prompt

```text
Continue the project from STEP 8.

IMPORTANT:
This step is for integration testing and fixing issues necessary for the required application only.

Do not deploy yet.
Do not add optional bonus functionality yet.

Test the complete end-to-end system.

FLOW 1 — DATA

Frontend
→ POST /api/data
→ Firestore
→ frontend refresh

Frontend
→ GET /api/data
→ display daily data

Frontend
→ PUT /api/data/{id}
→ Firestore
→ refresh

Frontend
→ DELETE /api/data/{id}
→ Firestore
→ refresh

FLOW 2 — SUMMARY

Frontend
→ GET /api/data/summary
→ FastAPI
→ Firestore
→ Analysis Service
→ Energy Summary
→ frontend

FLOW 3 — AI CHAT

Frontend
→ POST /api/chat
→ Chat Service
→ Summary Service
→ Energy Summary
→ Context Injection
→ OpenAI
→ AI response
→ frontend

FLOW 4 — CONVERSATION

Chat
→ save conversation
→ GET /api/conversations
→ list
→ GET /api/conversations/{id}
→ complete messages
→ frontend display

Test energy-specific questions:

1. "What is my average daily electricity consumption?"
2. "Which day had my highest consumption?"
3. "Which day had my lowest consumption?"
4. "Which month did I use the most electricity?"
5. "Do I use more electricity on weekdays or weekends?"
6. "Which day of the week has the highest average consumption?"
7. "Is my recent 7-day consumption higher than my overall average?"
8. "Has my electricity consumption been increasing?"
9. "What was my consumption on 2026-08-13?"
10. "What was my electricity consumption on 2026-09-01?"

Important:

- 2026-08-13 is inside the dataset period but may not exist in the injected summary.
- 2026-09-01 is outside the dataset period.

At this core stage, the AI must not invent either value.

Test:

- empty chat input
- invalid data
- invalid date
- nonexistent document
- backend unavailable
- Firestore error
- OpenAI error
- slow response
- empty dataset
- malformed API response

Fix only issues necessary for required functionality.

After testing:

1. Provide a complete system flow diagram.
2. Provide tested endpoints.
3. Provide PASS/FAIL test results.
4. Explain problems found and fixes.
5. Explain what remains before deployment.
6. Stop and wait.
```

---

# STEP 10 — Deployment + Documentation

## Prompt

```text
Continue the project from STEP 9.

IMPORTANT:
Only implement deployment preparation and final documentation.
Do not add major new functionality.

Prepare the application for production deployment.

BACKEND — Render

Prepare FastAPI for Render.

Verify:

- production start command
- environment variables
- Firebase credentials handling
- OpenAI API key handling
- CORS
- /health
- /docs
- production configuration
- error handling

FRONTEND — Vercel

Prepare the vanilla HTML/CSS/JavaScript frontend for Vercel.

Verify:

- production backend URL configuration
- API requests to Render
- CORS compatibility
- no frontend secrets
- static deployment compatibility

Consider environment/configuration values such as:

OPENAI_API_KEY
FIREBASE_SERVICE_ACCOUNT_JSON
API_BASE_URL
ALLOWED_ORIGINS

Use the actual architecture to determine any additional variables.

Do not put production secrets into source files.

README.md must document:

1. Project introduction
2. Problem statement
3. Why electricity consumption data is used
4. Raw dataset
5. Data period
6. 30-minute → daily aggregation
7. Data validation
8. Daily data model
9. Energy analysis summary
10. Summary limitations
11. Data flow
12. FastAPI endpoints
13. Firestore structure
14. Context Injection
15. Conversation history
16. Frontend
17. Environment variables
18. Local setup
19. Swagger
20. Render deployment
21. Vercel deployment
22. Security considerations
23. Estimated-cost limitations
24. Specific-date query limitation
25. Bonus features if implemented

Include an architecture diagram.

Use this conceptual flow:

Raw 30-minute data
→ preprocessing
→ daily consumption
→ Firestore
→ summary service
→ summary JSON
→ context injection
→ GPT
→ answer

For future/implemented Function Calling, document:

GPT
→ tool selection
→ backend validation
→ Firestore
→ tool result
→ GPT
→ answer

Before finishing:

1. Verify actual repository structure.
2. Verify README matches implementation.
3. Verify production URL configuration.
4. Verify backend /docs.
5. Verify frontend API communication.
6. Verify CRUD.
7. Verify summary.
8. Verify chat.
9. Verify conversation history.
10. Verify CORS.
11. Verify environment variables.
12. Verify no secrets are committed.

Do not claim deployment is complete unless it was actually performed and verified.

Finally provide:

- deployment checklist
- manual verification checklist
- remaining limitations

Stop after completing this step.
```

After commit and push, your GitHub repository becomes the source that Render and Vercel deploy from.

---

# BONUS 1 — Visualization / Export / Dark Mode

> Core Steps 1–10이 정상적으로 완료된 후 진행한다.

## Prompt

```text
The required electricity-consumption AI assistant is complete.

Now implement only the remaining optional UX/insight bonus features.

The following bonus features already exist:
- Daily electricity-consumption visualization
- Dark mode toggle
- Energy insights/statistics

Do NOT recreate or replace these features. Verify that they work correctly.

Focus on:

1. Data export:
   - CSV or JSON
   - export actual stored daily electricity-consumption data
   - do not export mock or hard-coded data

2. Improve the Daily Energy Data table UX:
   - use a reasonable fixed/max height with vertical scrolling
   - keep the table header visible while scrolling if practical
   - keep Add/Edit/Delete functionality unchanged
   - make the table usable on smaller screens

The existing visualization and insights must use actual application data and remain consistent with:

- daily value is kWh/day
- raw 30-minute Consumption values are not multiplied by 0.5 again
- dates use the application's local calendar interpretation

Do not break:

- CRUD
- summary
- chat
- context injection
- conversation history
- existing visualization
- existing dark mode
- deployment configuration

After implementation:

1. Verify the existing visualization, insights, and dark mode.
2. Explain the table UX changes.
3. Explain export behavior and exactly which data is exported.
4. Test all bonus features.
5. Stop.
```

---

# BONUS 2 — OpenAI Function Calling / Tool Use

## Prompt

```text
The required electricity-consumption AI assistant is complete.

Now implement the optional Function Calling / Tool Use bonus.

IMPORTANT DESIGN PRINCIPLE:

Context Injection remains the default.

If the summary contains enough information, GPT should answer from the summary and should NOT unnecessarily call a tool.

If the user asks for information that is not present in the summary, GPT may call an internal application tool.

For this project, consider these minimal tools:

1. get_data_summary
   - returns current energy summary

2. get_energy_data_by_date
   - retrieves actual daily electricity consumption for a specified local date

3. get_energy_data_by_period
   - retrieves daily consumption for a specified date range

4. get_energy_statistics
   - calculates requested statistics for a specific date range if truly useful

Use only tools that are actually necessary.

Do not create unnecessary tools.

IMPORTANT SECURITY/ARCHITECTURE RULES:

- GPT must never directly access Firestore.
- GPT can only call explicitly defined tools.
- Backend validates every tool argument.
- Tool implementations use the existing service/repository layer.
- Tool results come from actual Firestore data.
- Do not hard-code tool results.
- Do not fabricate missing dates.
- Do not return data outside the available dataset period.
- Do not log API keys or credentials.

Example:

User:
"What was my electricity consumption on 2026-08-13?"

Flow:

User
→ GPT
→ determine summary is insufficient
→ get_energy_data_by_date(date="2026-08-13")
→ backend validation
→ Firestore
→ tool result
→ GPT
→ final answer

For:

"Which month did I use the most electricity?"

If the summary already contains the answer:

User
→ GPT
→ Summary
→ final answer

Do not unnecessarily call Firestore.

The tool layer must validate:

- date format
- date range
- dataset boundary
- required arguments
- invalid/nonexistent records

Test at least:

1. Summary-only question.
2. Specific-date question.
3. Date-range question.
4. Nonexistent date.
5. Out-of-range date.
6. A question that should not call a tool.
7. A question that requires a tool.

For each test report:

- question
- whether a tool was called
- tool name
- arguments
- reason
- Firestore result
- final answer

Update README.md with:

- tool list
- schemas
- tool-selection logic
- context injection vs Function Calling
- complete tool-call flow
- validation/security
- examples

Stop after implementation and testing.
```

---

# BONUS 3 — MCP Server or GPT Actions

## Prompt

```text
The electricity-consumption AI assistant and Function Calling implementation are complete.

Now implement the remaining optional integration bonus from mission_statement.txt.

Before changing code:

1. Re-read the relevant mission requirement.
2. Inspect the existing architecture.
3. Explain the difference between:
   - REST API
   - OpenAI Function Calling
   - MCP Server
   - GPT Actions
4. Select the smallest and clearest option for this project.
5. Explain why.
6. Reuse existing services and business logic.
7. Do not unnecessarily rewrite the application.

The external interface should expose useful existing functionality such as:

- energy summary
- specific-date consumption
- date-range consumption/statistics

Do not duplicate business logic.

Document:

- architecture
- available tools/actions
- schemas
- authentication/security
- request/response flow
- example interaction
- external client usage

Conceptually:

AI Client
→ MCP / GPT Actions
→ application tool
→ FastAPI/service layer
→ Firestore
→ result
→ AI Client

Do not expose credentials.

Test at least one real electricity-consumption query.

After implementation:

1. Explain what was implemented.
2. Explain how it differs from Function Calling.
3. Show request/response flow.
4. Explain manual verification.
5. Update README.
6. Stop.
```

---

# FINAL AUDIT — Mission + Architecture + Data Analysis Verification

## Prompt

```text
Now perform a final audit of the entire project.

First read mission_statement.txt completely again.

Then inspect the actual implemented:

- backend
- frontend
- data/preprocessing
- analysis service
- Firestore integration
- API routes
- AI/chat service
- conversation service
- Function Calling if implemented
- bonus features if implemented
- tests
- configuration
- README

Do NOT assume something is complete merely because a file/function exists.

Verify actual behavior.

Return:

| Requirement | PASS/FAIL/PARTIAL | Evidence | Notes |
|---|---|---|---|

Audit required functionality:

1. 100+ time-series data points where required by mission
2. Electricity dataset preparation
3. Correct 30-minute → daily aggregation
4. Consumption is summed, not multiplied by 0.5
5. Local timezone/date handling
6. Daily data model
7. Data analysis
8. Summary
9. FastAPI
10. Pydantic validation
11. Firestore
12. POST /api/data
13. GET /api/data
14. PUT /api/data/{id}
15. DELETE /api/data/{id}
16. GET /api/data/summary
17. POST /api/chat
18. Context injection
19. Conversation saving
20. Conversation listing
21. Conversation loading
22. Conversation deletion
23. Vanilla HTML/CSS/JavaScript frontend
24. Chat UI
25. Data management UI
26. Summary UI
27. Conversation history UI
28. Render readiness
29. Vercel readiness
30. Environment variables
31. CORS
32. Swagger /docs
33. README
34. Security
35. Error handling

Audit the ENERGY ANALYSIS specifically:

- analysis period
- number of daily records
- total consumption
- average daily consumption
- minimum + date
- maximum + date
- monthly totals
- monthly averages
- month comparison
- weekday average
- weekend average
- weekday/weekend difference
- day-of-week averages
- highest/lowest day-of-week
- recent 7-day total/average
- recent 30-day total/average
- actual recent-period day counts
- recent-vs-overall comparison
- trend direction
- trend magnitude
- periods used for trend
- estimated cost statistics if implemented
- data-quality/coverage handling

Audit the AI boundary:

1. Does GPT receive a meaningful summary rather than all raw records?
2. Does the summary contain max/min dates?
3. Does it contain monthly statistics?
4. Does it contain weekday/weekend statistics?
5. Does it contain day-of-week statistics?
6. Does it contain recent statistics?
7. Does it contain trend information?
8. Does GPT avoid inventing information absent from the summary?
9. Are specific-date questions clearly separated from summary questions?
10. If Function Calling exists, does it query actual Firestore data?

Audit the complete conceptual data flow:

Raw 30-minute data
→ validation
→ local-date preprocessing
→ daily consumption
→ Firestore
→ analysis service
→ summary JSON
→ context injection
→ GPT
→ if sufficient: answer
→ if insufficient: Function Calling
→ backend validation
→ Firestore
→ tool result
→ GPT
→ answer

Audit bonuses separately:

BONUS 1
- visualization
- additional statistic
- CSV/JSON export
- dark mode

BONUS 2
- Function Calling
- internal energy tools
- tool argument validation
- actual Firestore lookup
- tool selection
- no unnecessary tool calls
- documentation

BONUS 3
- MCP or GPT Actions
- external integration
- security
- documentation

Important:

- Do not mark partially implemented functionality as PASS.
- Do not mark code that exists but does not work as PASS.
- Do not hide failures.
- Distinguish required features from bonuses.
- If something is FAIL/PARTIAL, explain exactly why.
- Prioritize fixes by severity.

At the end provide:

1. Overall completion status.
2. Required-feature failures.
3. Bonus-feature failures.
4. Highest-priority fixes.
5. Data-analysis issues.
6. AI hallucination/data-boundary issues.
7. Final manual test checklist.
```

---

# Learning Checkpoints

각 Step 이후 Antigravity가 코드를 만들었다는 사실보다 **내가 왜 그렇게 설계했는지를 설명할 수 있는지** 확인한다.

| Step | 이해해야 할 핵심 |
|---|---|
| 01 | 프로젝트 구조와 각 계층의 역할 |
| 02 | **30분 데이터 → local date → daily kWh → analysis → summary** |
| 03 | FastAPI, HTTP, REST, CRUD, Pydantic |
| 04 | Firestore document와 CRUD |
| 05 | Summary API와 analysis service의 분리 |
| 06 | **LLM + system prompt + context injection** |
| 07 | Conversation persistence |
| 08 | Vanilla JS + fetch + API integration |
| 09 | Full-stack integration testing |
| 10 | Environment variables, CORS, Render, Vercel, documentation |
| Bonus 1 | Visualization / export / UX |
| Bonus 2 | **Function Calling + tool use** |
| Bonus 3 | MCP 또는 GPT Actions |
| Final Audit | 실제 구현 상태와 mission 요구사항 검증 |

---

# 반드시 스스로 설명할 수 있어야 하는 질문

STEP 2 이후:

```text
왜 daily consumption은 SUM인가?

왜 30분 값에 0.5를 다시 곱하면 안 되는가?

왜 timezone을 보존해야 하는가?

왜 max와 max_date를 함께 저장하는가?

왜 모든 날짜를 summary에 넣지 않는가?

weekday/weekend 평균은 어떻게 계산하는가?

monthly total과 monthly average는 왜 둘 다 필요한가?

recent 7-day와 recent 30-day를 왜 따로 보는가?

trend는 왜 첫날과 마지막 날만 비교하면 위험한가?
```

STEP 5~6 이후:

```text
왜 summary service와 summary API를 분리하는가?

왜 모든 raw data를 GPT에게 보내지 않는가?

왜 system prompt에 summary를 넣는가?

summary에 없는 특정 날짜를 GPT가 답하면 왜 문제가 되는가?
```

Function Calling 이후:

```text
언제 Summary만으로 답하는가?

언제 Tool을 호출해야 하는가?

왜 GPT가 Firestore에 직접 접근하면 안 되는가?

tool argument validation은 왜 backend에서 해야 하는가?

왜 "2026-08-13" 같은 특정 날짜 질문은 tool의 좋은 예인가?
```

---

# Core Mental Model

최종적으로 이 프로젝트를 다음과 같이 이해하는 것이 목표다.

```text
                         RAW ENERGY DATA
                       30-minute readings
                               │
                               ▼
                       Data Validation
                               │
                               ▼
                     Local-date Processing
                               │
                               ▼
                    DAILY CONSUMPTION
                         kWh / day
                               │
                               ▼
                          Firestore
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
        Summary Service                Data Query Tools
                │                             │
                ▼                             │
        Energy Summary JSON                   │
                │                             │
                ▼                             │
        Context Injection                     │
                │                             │
                └──────────────┬──────────────┘
                               ▼
                              GPT
                               │
                    ┌──────────┴──────────┐
                    │                     │
             Summary sufficient?      Need details?
                    │                     │
                   YES                    NO
                    │                     │
                    ▼                     ▼
                 Answer             Function Calling
                                          │
                                          ▼
                                      Backend
                                          │
                                          ▼
                                      Firestore
                                          │
                                          ▼
                                      Tool Result
                                          │
                                          ▼
                                         GPT
                                          │
                                          ▼
                                        Answer
```

핵심은 다음 한 문장으로 요약할 수 있다.

> **데이터를 먼저 의미 있는 일별 데이터와 Summary로 분석하고, Summary로 충분한 질문은 GPT가 답하게 하며, Summary로 부족한 질문은 실제 Firestore 데이터를 Tool을 통해 조회하게 한다.**

---

# Recommended Execution Order

```text
STEP 1
Project Setup + Architecture
        ↓
STEP 2 ⭐
Energy Data Preparation + Analysis / Summary
        ↓
STEP 3
FastAPI + Pydantic
        ↓
STEP 4
Firestore + CRUD
        ↓
STEP 5
Data Summary API
        ↓
STEP 6 ⭐
OpenAI Chat + Context Injection
        ↓
STEP 7
Conversation History
        ↓
STEP 8
Vanilla Frontend
        ↓
STEP 9
Complete Integration Test
        ↓
STEP 10
Deployment + Documentation
        ↓
BONUS 1
Visualization / Export / Dark Mode
        ↓
BONUS 2 ⭐⭐
Function Calling
        ↓
BONUS 3
MCP / GPT Actions
        ↓
FINAL AUDIT
```

각 단계는 반드시:

```text
Antigravity
    ↓
코드 작성
    ↓
내가 코드 확인
    ↓
실행 / 테스트
    ↓
왜 이렇게 설계했는지 확인
    ↓
다음 Step
```

의 순서로 진행한다.


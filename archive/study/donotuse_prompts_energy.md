# Prompts to Antigravity CLI — Energy Consumption AI Assistant

이 문서는 `mission_statement.txt`의 과제를 **개인 에너지 사용량 데이터셋**으로 단계별 구현하기 위한 프롬프트입니다.

각 Step을 한 번에 하나씩 Antigravity CLI에 전달하고, 해당 Step의 결과를 직접 확인한 뒤 다음 Step으로 넘어갑니다.

---

# Project Data Context

이번 프로젝트에서 사용하는 데이터는 개인 전력 사용량 데이터입니다.

## Raw dataset

원본 데이터는 30분 단위이며 주요 컬럼은 다음과 같습니다.

```text
Consumption (kwh)
Estimated Cost Inc. Tax (p)
Standing Charge Inc. Tax (p)
Start
End
```

예:

```text
Consumption (kwh) | Estimated Cost Inc. Tax (p) | Standing Charge Inc. Tax (p) | Start                    | End
1.508              | 41.08                       | 0.91                         | 2026-03-01T09:00:00+09:00 | 2026-03-01T09:30:00+09:00
0.436              | 11.88                       | 0.91                         | 2026-03-01T09:30:00+09:00 | 2026-03-01T10:00:00+09:00
0.044              | 1.20                        | 0.91                         | 2026-03-01T10:00:00+09:00 | 2026-03-01T10:30:00+09:00
```

데이터 범위:

**2026-03-01 ~ 2026-08-31**

중요한 데이터 의미:

- `Consumption (kwh)`는 해당 30분 구간에서 실제로 사용한 에너지량(kWh)이다.
- 따라서 일별 사용량은 같은 날짜의 30분 단위 `Consumption (kwh)`를 합산하여 계산한다.
- 30분 단위 값에 다시 0.5를 곱하지 않는다.
- 애플리케이션의 주요 시계열 데이터 단위는 **일별 전력 사용량(kWh/day)** 으로 한다.
- 원본 데이터는 가능한 한 보존하고, 별도의 전처리 결과로 일별 데이터를 생성한다.
- `Estimated Cost Inc. Tax (p)`와 `Standing Charge Inc. Tax (p)`는 비용 분석에 사용할 수 있지만, 실제 청구 금액과 정확히 동일하다고 가정하지 않는다. 비용 관련 통계에는 데이터의 `Estimated` 특성을 명확히 표시한다.
- 시간대는 데이터의 timezone 정보를 존중한다. 날짜를 추출할 때 UTC로 무조건 변환하여 날짜가 바뀌지 않도록 주의한다.

## AI assistant의 목표

최종 서비스는 사용자의 전력 사용량 데이터를 이해하고 다음과 같은 질문에 답할 수 있는 AI assistant가 된다.

예:

- "내 하루 평균 전력 사용량은 얼마야?"
- "3월부터 8월까지 전기를 얼마나 사용했어?"
- "전력 사용량이 가장 많았던 날은 언제야?"
- "전력 사용량이 가장 적었던 날은 언제야?"
- "어느 달에 전기를 가장 많이 사용했어?"
- "평일과 주말 중 언제 전기를 더 많이 사용해?"
- "어느 요일에 전기를 가장 많이 사용해?"
- "최근 7일 사용량이 전체 평균보다 높아?"
- "최근 30일 사용량은 증가하고 있어?"
- "최근 몇 달 동안 사용량이 어떻게 변했어?"
- "2026년 8월 13일에는 전기를 얼마나 사용했어?"

중요한 원칙:

> **Summary에 없는 정보를 LLM이 추측하도록 하지 않는다.**

특히 특정 날짜의 상세 데이터처럼 summary에 포함되지 않은 정보는 나중에 Function Calling/tool을 통해 실제 Firestore 데이터를 조회할 수 있도록 설계한다.

---

# Development Roadmap

```text
STEP 1  → Project setup + architecture
STEP 2  → Energy data preparation + analysis/summary
STEP 3  → FastAPI + Pydantic
STEP 4  → Firestore + Data CRUD
STEP 5  → Data Summary API
STEP 6  → OpenAI Chat + Context Injection
STEP 7  → Conversation History
STEP 8  → Frontend
STEP 9  → Connect & test the complete application
STEP 10 → Deployment + documentation

BONUS 1 → Visualization / CSV or JSON export / Dark mode
BONUS 2 → Function Calling
BONUS 3 → MCP Server or GPT Actions
```

**IMPORTANT:** 각 Step은 독립적으로 확인한다. 현재 Step에서 요청하지 않은 미래 기능을 미리 구현하지 않는다.

---

# STEP 1 — Project Setup & Architecture

```text
You are helping me build an educational AI Native project step by step.

First, read the entire mission_statement.txt in this repository and use it as the authoritative specification for the project.

The project is an AI assistant based on my personal electricity consumption data.

DATA CONTEXT:

- Raw data is measured every 30 minutes.
- Data period: 2026-03-01 through 2026-08-31.
- Main raw columns:
  - Consumption (kwh)
  - Estimated Cost Inc. Tax (p)
  - Standing Charge Inc. Tax (p)
  - Start
  - End
- Consumption (kwh) represents the energy consumed during that 30-minute interval.
- Therefore, daily consumption is calculated by summing all 30-minute Consumption (kwh) values belonging to the same local calendar date.
- The application's main time-series unit will be daily electricity consumption in kWh/day.

The final application should satisfy the requirements in mission_statement.txt, including:

1. Store time-series data in Firebase Firestore.
2. Provide CRUD APIs through FastAPI.
3. Calculate a useful data summary.
4. Inject the summary into an OpenAI GPT system prompt.
5. Provide an AI chat interface.
6. Save and load conversation history.
7. Use a vanilla HTML/CSS/JavaScript frontend.
8. Deploy the backend on Render and frontend on Vercel.
9. Implement the optional bonus features after the core application works.

IMPORTANT DEVELOPMENT RULE:

We are building this project STEP BY STEP.

For STEP 1 only:

1. Inspect the current project directory.
2. Read mission_statement.txt completely.
3. Create a clean project structure for:
   - backend
   - frontend
   - data
4. Create the basic FastAPI application.
5. Create requirements.txt with the required packages:
   - fastapi
   - uvicorn
   - firebase-admin
   - openai
   - python-dotenv
6. Create an appropriate .gitignore.
7. Create a .env.example showing the environment variables we will eventually need.
8. Configure the basic FastAPI application and CORS structure, but do not implement actual application APIs yet.
9. Create placeholder folders/files for routers, services, models, and database configuration if appropriate.
10. Create a basic health-check endpoint such as GET /health.
11. Make sure the FastAPI application can run locally.

Do NOT:
- implement Firestore CRUD
- implement OpenAI
- implement chat
- implement conversation history
- build the frontend
- implement data analysis
- implement Function Calling
- implement MCP
- deploy anything

After completing STEP 1:

1. Show me the final directory tree.
2. Explain the purpose of each important file.
3. Explain how to run the FastAPI server locally.
4. Tell me exactly what you implemented.
5. Tell me what remains for STEP 2.
6. Stop and wait for my instruction.
```

---

# STEP 2 — Energy Data Preparation & Analysis ⭐

이 단계에서는 **가장 중요한 데이터 분석 설계**를 먼저 이해하고 확인합니다.

```text
Continue the AI Native project from STEP 1.

IMPORTANT:
Only implement STEP 2. Do not implement later steps.

First inspect the actual energy dataset file in the repository. Do not assume its filename.

DATA:

- Date range: 2026-03-01 through 2026-08-31.
- Raw interval: 30 minutes.
- Columns:
  - Consumption (kwh)
  - Estimated Cost Inc. Tax (p)
  - Standing Charge Inc. Tax (p)
  - Start
  - End

IMPORTANT DATA SEMANTICS:

- Consumption (kwh) is already the energy consumed during the 30-minute interval.
- Daily consumption = SUM of all 30-minute Consumption (kwh) values for that local calendar date.
- Do NOT multiply each Consumption value by 0.5 again.
- Preserve the timezone-aware timestamp information when determining the local calendar date.

For STEP 2:

## Part A — Inspect and validate the raw data

Determine:

1. Actual filename and location.
2. Number of rows.
3. Actual columns and data types.
4. Minimum and maximum timestamp.
5. Missing values.
6. Duplicate records.
7. Invalid numeric values.
8. Whether each normal day contains approximately 48 half-hour records.
9. Whether any dates or intervals are missing.
10. Whether there are any unexpected gaps or anomalies.

Do not silently repair suspicious data. Report important anomalies.

## Part B — Create the daily dataset

Create a reusable preprocessing workflow that converts the raw 30-minute dataset into daily records.

At minimum:

- date
- daily_consumption_kwh

If the cost fields can be meaningfully aggregated, also calculate appropriate daily cost fields and document exactly what they mean.

Do not claim estimated cost is the same as an actual bill.

## Part C — Create a reusable analysis/summary service

Create a reusable analysis module/function that produces structured Python data suitable for later JSON serialization.

The goal is NOT just to calculate total/average/min/max.

The summary should contain enough information for the AI assistant to answer useful energy-consumption questions.

The summary should consider these categories:

### 1. Overall statistics

- analysis period
- number of daily records
- total consumption
- average daily consumption
- minimum daily consumption + date
- maximum daily consumption + date

### 2. Monthly statistics

Calculate for each month in the dataset:

- total consumption
- average daily consumption
- number of days

Also identify:

- month with the highest total consumption
- month with the highest average daily consumption
- month with the lowest relevant metric where appropriate

This supports questions such as:

- "Which month did I use the most electricity?"
- "How did August compare with July?"
- "What was my average daily usage in May?"

### 3. Weekday vs weekend

Calculate:

- weekday average daily consumption
- weekend average daily consumption
- difference
- percentage difference where meaningful

This supports:

- "Do I use more electricity on weekdays or weekends?"

### 4. Day-of-week patterns

Calculate average consumption for:

- Monday
- Tuesday
- Wednesday
- Thursday
- Friday
- Saturday
- Sunday

Identify the highest and lowest average weekday.

This supports:

- "Which day of the week do I use the most electricity?"

### 5. Recent-period statistics

Calculate at least:

- recent 7-day total and average
- recent 30-day total and average

Also compare recent averages with the overall average.

This supports:

- "Is my recent usage higher than usual?"
- "Have I been using more electricity recently?"

Be careful if the dataset contains fewer than 30 days; use the available data and explicitly report the actual number of days used.

### 6. Trend

Create a transparent trend calculation.

Prefer a meaningful comparison such as monthly average consumption or comparable recent-vs-earlier period averages rather than blindly comparing the first and last individual day.

Return:

- trend direction: increasing / decreasing / stable
- percentage change or other useful magnitude
- the periods used for the comparison

Document the calculation method.

### 7. Cost statistics

If the cost fields are reliable enough to aggregate, include useful estimated cost statistics separately from consumption statistics.

Do not mix pence and pounds without clearly documenting the unit.

Do not describe estimated costs as confirmed actual billing amounts.

## VERY IMPORTANT — Summary limitations

The summary should NOT attempt to contain every individual day's raw record.

For example, if the summary contains:

max_daily_consumption_kwh = 82.4
max_date = 2026-07-21

then the AI can answer:
"When was my highest-consumption day?"

But if the summary does not contain the value for 2026-08-13, the AI should NOT invent that value.

A specific-date question such as:
"What was my consumption on 2026-08-13?"

should later be handled by a database query / Function Calling tool.

Design the summary with this distinction in mind.

## Output structure

Use a clear structured summary, conceptually similar to:

{
  "period": {...},
  "count": ...,
  "overall": {...},
  "monthly": {...},
  "weekday_weekend": {...},
  "day_of_week": {...},
  "recent": {...},
  "trend": {...},
  "extremes": {...},
  "cost": {...}
}

The exact field names can follow the project's coding style, but preserve the meaning.

Do NOT connect the summary to Firestore yet.
Do NOT connect it to OpenAI yet.
Do NOT build the frontend yet.
Do NOT implement Function Calling yet.

Use pandas where appropriate.

After completing STEP 2:

1. Show the raw-data validation results.
2. Show the preprocessing flow:
   30-minute data → daily data → analysis summary
3. Show the actual number of raw records and daily records.
4. Show whether any dates/intervals are missing.
5. Show an example of the actual generated summary using the project's data.
6. Explain each major summary field.
7. Give 10–15 example user questions that the summary can answer.
8. Give examples of questions that the summary cannot answer without an additional database query.
9. Explain why those questions require additional data retrieval.
10. Tell me exactly what files you created or modified.
11. Stop and wait.
```

---

# STEP 3 — FastAPI + Pydantic

```text
Continue the project from STEP 2.

IMPORTANT:
Only implement STEP 3. Do not implement later steps.

For STEP 3, build the FastAPI API structure and Pydantic request/response models.

Create a clean separation between:

- routers
- services
- models

The main application data represents DAILY electricity consumption.

The mission requires the data API to support the conceptual structure:

(date, value, memo)

For this project:
- date = local calendar date
- value = daily electricity consumption in kWh
- memo = optional user note

Prepare Pydantic models for:

- creating data
- updating data
- returning data
- returning summary information

Implement the required API routes:

POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}
GET    /api/data/summary

However, at this stage DO NOT connect to Firestore.

Use temporary in-memory data or another clearly marked temporary implementation so I can test the API behavior.

Also:

1. Add appropriate HTTP status codes.
2. Add basic validation.
3. Add reasonable error handling.
4. Make Swagger UI available at /docs.
5. Keep API logic separate from router logic.
6. Reuse the analysis model/service structure from STEP 2 where appropriate.
7. Do not implement OpenAI.
8. Do not implement conversation history.
9. Do not build the frontend.
10. Do not deploy.

After implementation:

1. Explain REST API, CRUD, and Pydantic in terms of this energy project.
2. Show the endpoint table.
3. Explain one complete request/response example.
4. Tell me how to test the endpoints using Swagger.
5. Tell me which parts are temporary and will be replaced by Firestore in STEP 4.
6. Stop and wait.
```

---

# STEP 4 — Firestore + Data CRUD

```text
Continue the project from STEP 3.

IMPORTANT:
Only implement STEP 4. Do not implement later steps.

Connect the FastAPI backend to Firebase Firestore.

Requirements:

1. Configure Firebase Admin SDK.
2. Use environment variables for Firebase credentials.
3. Never hard-code credentials.
4. Create a Firestore collection named:
   data
5. Store DAILY electricity consumption records.
6. Keep the conceptual mission structure:
   date
   value
   memo

For this project:
- value means daily electricity consumption in kWh.

Implement:

POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}

Replace the temporary in-memory implementation from STEP 3 with Firestore.

Keep database logic separated from router logic.

Handle:

- document not found
- invalid input
- database errors

Keep existing Pydantic validation.

Do not implement:
- OpenAI
- chat
- conversation history
- frontend
- Function Calling
- MCP
- deployment

After implementation:

1. Explain the Firestore structure.
2. Show an example daily-energy document.
3. Explain how POST, GET, PUT and DELETE map to Firestore operations.
4. Explain how environment variables protect Firebase credentials.
5. Explain how to test CRUD through Swagger.
6. Tell me what changed compared with STEP 3.
7. Stop and wait.
```

---

# STEP 5 — Data Summary API

```text
Continue the project from STEP 4.

IMPORTANT:
Only implement STEP 5. Do not implement later steps.

Implement:

GET /api/data/summary

The summary must be generated from the actual daily electricity-consumption data stored in Firestore.

Reuse the analysis/summary service created in STEP 2 rather than duplicating the analysis logic inside the router.

The summary should include the important energy-specific analysis designed in STEP 2:

1. period
2. count
3. total consumption
4. average daily consumption
5. minimum daily consumption + date
6. maximum daily consumption + date
7. monthly statistics
8. weekday vs weekend statistics
9. day-of-week statistics
10. recent 7-day statistics
11. recent 30-day statistics
12. recent-vs-overall comparison
13. trend
14. estimated cost statistics if reliably available

Important:

- Do not hard-code example values.
- Use actual Firestore data.
- Return clean JSON.
- Use a Pydantic response model where appropriate.
- Handle empty datasets gracefully.
- Do not include every individual daily record merely to make the summary larger.
- Do not implement OpenAI.
- Do not implement conversation history.
- Do not build the frontend.

After implementation:

1. Show an example JSON response using actual project data.
2. Explain exactly how each major metric is calculated.
3. Explain why the summary contains max_date/min_date rather than only max/min.
4. Explain why monthly, weekday/weekend, day-of-week, recent and trend information is included.
5. Explain why a specific-date question may still require a direct database query.
6. Explain how /api/chat will later use this endpoint/service.
7. Stop and wait.
```

---

# STEP 6 — OpenAI Chat + Context Injection ⭐

```text
Continue the project from STEP 5.

IMPORTANT:
Only implement STEP 6. Do not implement conversation persistence, frontend, Function Calling, or MCP yet.

Implement:

POST /api/chat

The request should contain a user's natural-language question.

The chat flow must be:

1. Receive the user's question.
2. Obtain the current energy-data summary from the summary service.
3. Construct a system prompt containing the summary.
4. Send the system prompt + user question to the OpenAI API.
5. Receive the GPT response.
6. Return the AI response as JSON.

The system prompt should establish that the AI is an electricity-consumption data assistant.

The prompt must contain the actual summary, including relevant fields such as:

- analysis period
- total consumption
- average daily consumption
- maximum/minimum consumption and their dates
- monthly statistics
- weekday/weekend comparison
- day-of-week patterns
- recent 7-day/30-day statistics
- trend
- cost statistics if available

IMPORTANT ANTI-HALLUCINATION RULES:

1. Use only information contained in the provided summary.
2. Do not invent values, dates, trends, or costs.
3. Do not claim to know a specific day's consumption if that day's value is not present in the summary.
4. If the question requires information that is not available in the summary, clearly say that the current summary does not contain enough information.
5. Do not fabricate data for dates outside 2026-03-01 through 2026-08-31.
6. Use kWh for energy consumption.
7. Clearly distinguish estimated cost from confirmed billing amounts.

For example, if the summary contains:

max_daily_consumption_kwh = 82.4
max_date = 2026-07-21

the AI can answer:
"When was my highest-consumption day?"

But if the summary does not contain the value for 2026-08-13, the AI must not invent it.

Architectural requirement:

Do NOT put all chat logic inside the router.

Use a chat service.

Conceptually:

Frontend
↓
POST /api/chat
↓
Chat Router
↓
Chat Service
↓
Summary Service
↓
System Prompt + Energy Summary
↓
OpenAI API
↓
AI Answer

Use OPENAI_API_KEY from environment variables.

Do not expose the API key to frontend JavaScript.

Add reasonable error handling for OpenAI API failures.

After implementation:

1. Show the request/response format.
2. Show an example generated system prompt using the actual energy summary.
3. Explain context injection in simple terms.
4. Explain why the OpenAI API key belongs in the backend.
5. Explain the complete /api/chat flow.
6. Test at least these questions:
   - "What is my average daily electricity consumption?"
   - "Which day had the highest consumption?"
   - "Do I use more electricity on weekdays or weekends?"
   - "Which month had the highest consumption?"
   - "Has my recent consumption been increasing?"
7. Also test a question requiring information not present in the summary, such as a specific date, and verify that the AI does not invent an answer.
8. Tell me what you implemented.
9. Stop and wait.
```

---

# STEP 7 — Conversation History

```text
Continue the project from STEP 6.

IMPORTANT:
Only implement STEP 7. Do not build the frontend or deploy yet.

Implement conversation history using Firestore.

Create the collection:

conversations

Implement:

POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}

A conversation should contain:

- conversation ID
- title or name
- created_at
- updated_at if useful
- messages

Each message should contain:

- role
- content

Roles should support at least:

- user
- assistant

Modify /api/chat so that completed conversations are automatically saved according to the mission requirements.

Keep conversation logic in a dedicated conversation service.

Important:

1. Do not expose credentials.
2. Validate request data with Pydantic.
3. Handle missing conversation IDs.
4. Make sure a conversation can be retrieved with its complete message history.
5. Keep existing data CRUD and summary functionality working.
6. Do not build the frontend.
7. Do not implement Function Calling.
8. Do not implement MCP.
9. Do not deploy.

After implementation:

1. Show the Firestore conversation document structure.
2. Explain how a chat becomes a saved conversation.
3. Explain how the frontend will later load an old conversation.
4. Explain what changed in /api/chat.
5. Test the endpoints.
6. Stop and wait.
```

---

# STEP 8 — Vanilla Frontend

```text
Continue the project from STEP 7.

IMPORTANT:
Only implement STEP 8. Do not deploy yet.

Build the frontend using ONLY:

- HTML
- CSS
- vanilla JavaScript

Do not use React, Vue, Next.js, or another frontend framework.

Create a clean, modern dashboard for the Electricity Consumption AI Assistant.

The UI should contain:

## 1. AI CHAT

- message input
- send button
- conversation display
- loading indicator
- clear distinction between user and AI messages
- error display

Example user questions can relate to electricity consumption.

## 2. CONVERSATION HISTORY

- list previous conversations
- click a conversation
- load its messages
- display the selected conversation

## 3. DATA MANAGEMENT

Display the daily energy data.

Support:
- adding a data record
- listing data
- at least one visible CRUD operation
- ideally add/edit/delete

For the data form, make it clear that:

value = daily electricity consumption in kWh.

## 4. DATA SUMMARY

Display useful current summary information, including:

- analysis period
- number of daily records
- total consumption
- average daily consumption
- maximum/minimum consumption and dates
- recent usage
- weekday/weekend comparison
- trend
- other useful statistics

Create a clean responsive design.

Important:

1. Keep JavaScript separated into sensible files where practical.
2. Put API communication in a dedicated JavaScript module where practical.
3. Do not put API keys in frontend code.
4. Use the backend API.
5. Do not hard-code fake AI responses.
6. Do not deploy yet.

At the end:

1. Show the frontend directory structure.
2. Explain how each UI section communicates with FastAPI.
3. Explain the JavaScript fetch calls.
4. Explain loading/error states.
5. Tell me how to run the frontend locally.
6. Stop and wait.
```

---

# STEP 9 — Connect & Test the Complete Application

```text
Continue the project from STEP 8.

IMPORTANT:
This step is for integration testing and fixing necessary issues only.
Do not deploy yet.
Do not add bonus functionality yet.

Test the complete application end-to-end.

## FLOW 1 — Data CRUD

Frontend
→ POST /api/data
→ Firestore
→ frontend refresh

Frontend
→ GET /api/data
→ display daily energy data

Frontend
→ PUT /api/data/{id}
→ Firestore
→ frontend refresh

Frontend
→ DELETE /api/data/{id}
→ Firestore
→ frontend refresh

## FLOW 2 — Summary

Frontend
→ GET /api/data/summary
→ FastAPI
→ Firestore
→ energy summary calculation
→ frontend display

## FLOW 3 — AI CHAT

Frontend
→ POST /api/chat
→ summary retrieval
→ context injection
→ OpenAI
→ AI response
→ frontend display

## FLOW 4 — Conversation history

Chat
→ conversation saved
→ GET /api/conversations
→ conversation list
→ GET /api/conversations/{id}
→ messages displayed

## Test energy-specific AI questions

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

The last two tests are important:

- 2026-08-13 is inside the dataset period but may not be in the summary.
- 2026-09-01 is outside the dataset period.

The AI must not invent either value.

Test common errors:

- empty input
- invalid data
- nonexistent document
- backend unavailable
- OpenAI API error
- Firestore error
- slow response

Fix only issues necessary for required functionality.

After testing:

1. Give me a complete system flow diagram.
2. Give me a list of tested endpoints.
3. Tell me what problems you found and fixed.
4. Tell me what still needs to be done before deployment.
5. Stop and wait.
```

---

# STEP 10 — Deployment + README

```text
Continue the project from STEP 9.

IMPORTANT:
This is the deployment and documentation step.
Do not add major new functionality.

Prepare the application for production deployment.

## BACKEND — Render

- Deploy FastAPI to Render.
- Make sure the production server starts correctly.
- Configure production environment variables.
- Configure CORS for the Vercel frontend.
- Make sure /docs works on the deployed backend.
- Do not expose secrets.
- Consider Render free-tier cold starts and provide an appropriate user-facing note if necessary.

## FRONTEND — Vercel

- Prepare the vanilla HTML/CSS/JavaScript frontend for Vercel.
- Configure the production backend URL through an appropriate environment/configuration mechanism for a vanilla frontend deployment.
- Make sure the frontend communicates with the Render backend.

## README

Create/update README.md containing:

1. Project introduction
2. Problem statement
3. Why electricity consumption data was selected
4. Raw data description
5. Data period: 2026-03-01 ~ 2026-08-31
6. 30-minute → daily aggregation method
7. Main features
8. Architecture
9. Technology stack
10. Directory structure
11. API endpoint table
12. Firestore structure
13. Energy-data summary structure
14. Context-injection architecture
15. Conversation history
16. Local installation
17. Environment variables
18. Backend deployment
19. Frontend deployment
20. Swagger URL
21. Limitations
22. Security considerations
23. AI summary limitations
24. How specific-date questions are handled
25. Bonus features if implemented

Also include a simple architecture diagram.

Do not put actual API keys or Firebase credentials in README.

Before finishing:

1. Verify production URLs.
2. Verify backend /docs.
3. Verify frontend chat.
4. Verify data CRUD.
5. Verify summary.
6. Verify conversation history.
7. Verify environment variables.
8. Verify CORS.

Finally, give me a deployment checklist and tell me exactly what I should manually verify.

Stop after completing this step.
```

---

# BONUS 1 — Visualization / Export / Dark Mode

**Only after the required project is complete and working.**

```text
The required electricity-consumption AI assistant is now complete.

Implement the OPTIONAL BONUS features only.

Add:

1. At least one useful electricity-consumption visualization.
   - Prefer a daily or monthly consumption trend chart.
   - The chart must use actual application data.
   - Make the trend/changes easy to understand.

2. At least one additional useful statistical metric that is not already shown in the core summary.

3. Data export:
   - CSV or JSON download.
   - Export the stored daily electricity-consumption data.

4. Dark mode toggle.

Keep the existing architecture clean.

Do not break:

- CRUD
- summary
- chat
- context injection
- conversation history
- deployment

After implementation:

1. Explain each bonus feature.
2. Explain what data the chart uses.
3. Explain the additional metric.
4. Explain how export works.
5. Explain how dark mode works.
6. Stop.
```

---

# BONUS 2 — OpenAI Function Calling ⭐

이 보너스에서는 **summary만으로 부족한 질문을 실제 데이터 조회 tool로 해결**합니다.

```text
The required electricity-consumption AI assistant is complete.

Now implement the OPTIONAL Function Calling bonus from mission_statement.txt.

The goal is to allow GPT to decide when it needs an internal application tool instead of relying only on the injected summary.

IMPORTANT DESIGN PRINCIPLE:

Context Injection remains the default.

If the summary already contains enough information, GPT should answer from the summary and should not unnecessarily call a tool.

If the user asks for information not present in the summary, GPT may call an appropriate internal tool.

For this electricity project, design tools such as:

1. get_data_summary
   - returns the current energy-consumption summary

2. get_energy_data_by_date
   - retrieves actual daily electricity consumption for a specified date

3. get_energy_data_by_period
   - retrieves daily electricity-consumption data for a specified date range

4. get_energy_statistics
   - calculates statistics for a requested date range if useful

Use only the tools that are actually necessary. Do not create unnecessary tools.

Example:

User:
"What was my electricity consumption on 2026-08-13?"

Possible flow:

User
→ GPT
→ determine that summary does not contain the requested date
→ call get_energy_data_by_date(date="2026-08-13")
→ FastAPI validates the argument
→ Firestore query
→ tool result
→ GPT
→ final answer

For:

"Which month did I use the most electricity?"

the summary may already contain the answer, so GPT should normally answer without an unnecessary database tool call.

IMPORTANT:

- GPT must never directly access Firestore.
- GPT can only call explicitly defined tools.
- Backend validates every tool argument.
- Tool implementations query actual Firestore data.
- Tool results are returned to GPT.
- GPT generates the final natural-language response.
- Do not hard-code tool calls for every question.
- Do not fabricate tool results.
- Do not return data outside the available dataset period.
- If a requested date does not exist, return an appropriate result instead of inventing a value.

The dataset period is:

2026-03-01 through 2026-08-31.

Test at least:

1. Summary-only question:
   "What is my average daily electricity consumption?"

2. Specific-date question:
   "What was my electricity consumption on 2026-08-13?"

3. Period query:
   "Show me the daily consumption from 2026-08-01 to 2026-08-07."

4. Invalid/out-of-range date:
   "What was my consumption on 2026-09-01?"

5. A question that should not require a tool because the summary already contains the answer.

Make it possible to understand:

- which tool was called
- the arguments
- why it was needed
- the tool result
- the final answer

Do not log API keys or sensitive credentials.

Update README.md with:

1. Available tools
2. Tool schemas
3. When each tool is used
4. Example tool-call flow
5. Why a tool was selected
6. Difference between context injection and Function Calling

After implementation, explain the architecture and stop.
```

---

# BONUS 3 — MCP Server or GPT Actions

`mission_statement.txt`에서는 Function Calling과 함께 **MCP Server 또는 GPT Actions 중 하나의 방식으로 동일 기능을 외부 채널/클라이언트에서 호출하는 것**을 보너스로 요구합니다.

```text
The electricity-consumption AI assistant and Function Calling implementation are complete.

Now implement the remaining optional bonus requirement from mission_statement.txt:

Connect the same internal functionality through either:

- MCP Server
OR
- GPT Actions

Before changing code:

1. Inspect the existing architecture.
2. Read the relevant mission_statement.txt requirement again.
3. Explain the difference between:
   - normal REST API
   - OpenAI Function Calling
   - MCP Server
   - GPT Actions
4. Decide which option is the smallest and clearest implementation for this project.
5. Explain why you selected it.
6. Do not rewrite the existing application unnecessarily.

The external tool/client should be able to access useful electricity-data functionality such as:

- data summary
- specific-date energy consumption
- date-range energy data/statistics

Use the existing backend/service logic where practical.

Do not duplicate business logic unnecessarily.

Document:

- architecture
- available tools/actions
- schemas
- authentication/security considerations
- request/response flow
- example interaction
- how the external client calls the functionality

README.md must explain the complete flow with a simple diagram.

For example:

AI Client
→ MCP / GPT Actions
→ application tool
→ FastAPI/service layer
→ Firestore
→ result
→ AI Client

Do not expose credentials.

Test the external integration with at least one real electricity-consumption query.

After implementation:

1. Explain what was implemented.
2. Explain how it differs from normal Function Calling.
3. Show the request/response flow.
4. Show what I should manually verify.
5. Stop.
```

---

# FINAL AUDIT — Mission Requirement Check

모든 기능이 끝난 후 마지막으로 실행합니다.

```text
Now perform a final audit of the entire project.

First read mission_statement.txt completely again.

Then inspect the actual implemented code, configuration, frontend, README, and tests.

Do NOT assume a requirement is complete just because a file or function exists.

Verify actual functionality.

Return a table:

| Requirement | PASS/FAIL | Evidence |
|---|---|---|

Check the required mission items:

1. 100+ time-series data points
2. Electricity dataset preparation
3. Daily aggregation from 30-minute Consumption (kwh)
4. Data analysis and summary
5. FastAPI
6. Pydantic validation
7. Firestore
8. POST /api/data
9. GET /api/data
10. PUT /api/data/{id}
11. DELETE /api/data/{id}
12. GET /api/data/summary
13. POST /api/conversations
14. GET /api/conversations
15. GET /api/conversations/{id} or equivalent conversation-loading mechanism
16. DELETE /api/conversations/{id}
17. POST /api/chat
18. Context injection
19. Automatic conversation saving
20. Vanilla HTML/CSS/JavaScript frontend
21. Chat UI
22. Data management UI
23. Conversation history UI
24. Summary UI
25. Render deployment readiness
26. Vercel deployment readiness
27. Swagger /docs
28. Environment variables
29. CORS
30. README
31. Security and basic error handling

Then audit bonuses separately:

BONUS 1:
- visualization
- additional statistic
- CSV/JSON export
- dark mode

BONUS 2:
- OpenAI Function Calling
- internal energy-data tools
- tool argument validation
- actual Firestore lookup
- tool selection based on need
- README documentation

BONUS 3:
- MCP Server OR GPT Actions
- external tool/client call verified
- README documentation

Also specifically verify the energy-analysis design:

- overall statistics
- max/min dates
- monthly statistics
- weekday/weekend comparison
- day-of-week patterns
- recent 7-day statistics
- recent 30-day statistics
- recent-vs-overall comparison
- trend
- cost statistics if implemented

Important:

- Do not mark something PASS if it is only partially implemented.
- Do not mark something PASS if it exists but does not work.
- Do not hide failures.
- Distinguish required functionality from bonus functionality.
- If something fails, explain exactly what needs to be fixed and why.

At the end provide:

1. Overall completion status.
2. Required-feature failures.
3. Bonus-feature failures.
4. Highest-priority fixes.
5. A final manual test checklist for me.
```

---

# Learning Checkpoints

각 Step이 끝날 때 다음 내용을 스스로 설명할 수 있는지 확인합니다.

| Step | 내가 이해해야 할 것 |
|---|---|
| **1** | 프로젝트 구조, backend/frontend 역할 |
| **2** ⭐ | **30분 데이터 → 일별 데이터 → 분석 → summary** |
| **3** | HTTP, REST API, CRUD, Pydantic |
| **4** | Firestore document와 database CRUD |
| **5** ⭐ | **왜 단순 total/average만으로는 부족한지** |
| **6** ⭐⭐ | **LLM + system prompt + context injection** |
| **7** | Conversation persistence |
| **8** | JavaScript + fetch + API |
| **9** | Full-stack integration |
| **10** | CORS, environment variables, deployment |
| **Bonus 1** | Visualization / export / UX |
| **Bonus 2** ⭐⭐ | **Function Calling + tool use** |
| **Bonus 3** | MCP 또는 GPT Actions |

---

# Core Mental Model

최종적으로 이 프로젝트를 다음과 같이 이해하는 것이 목표입니다.

```text
                  RAW ENERGY DATA
                30-minute readings
                       │
                       ▼
               Data Preprocessing
                       │
                       ▼
              Daily Consumption
                  (kWh/day)
                       │
                       ▼
                 Firestore
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   Summary Service            Data Query Tools
          │                         │
          ▼                         │
    Energy Summary                  │
          │                         │
          ▼                         │
   Context Injection                │
          │                         │
          └──────────┬──────────────┘
                     ▼
                    GPT
                     │
          ┌──────────┴──────────┐
          │                     │
     Summary enough?        Need details?
          │                     │
         YES                    NO
          │                     │
          ▼                     ▼
       Answer             Function Calling
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

핵심은 **모든 원본 데이터를 GPT에 보내는 것이 아니라**, 먼저 우리가 데이터를 분석하여 AI가 자주 필요로 하는 의미 있는 정보를 summary로 만들고, summary만으로 부족한 질문은 나중에 Function Calling을 통해 실제 데이터를 조회하도록 하는 것입니다.

---

# Recommended Learning Process

각 Prompt를 실행한 뒤 바로 다음 Prompt로 넘어가지 않습니다.

```text
Antigravity
     ↓
코드 작성
     ↓
YOU inspect code
     ↓
YOU run/test
     ↓
YOU ask "why?"
     ↓
이해
     ↓
NEXT STEP
```

예를 들어 STEP 2가 끝난 뒤에는:

```text
"왜 daily consumption을 sum으로 계산하나요?"

"왜 max와 함께 max_date가 필요한가요?"

"왜 모든 날짜의 데이터를 summary에 넣지 않았나요?"

"weekday/weekend 평균은 어떻게 계산했나요?"

"trend는 정확히 어떤 기준으로 increasing이라고 판단하나요?"

"어떤 질문은 summary로 답할 수 있고 어떤 질문은 Function Calling이 필요한가요?"
```

와 같은 질문을 Antigravity CLI에게 해보는 것을 권장합니다.

이렇게 하면 단순히 **AI가 코드를 만들어준 프로젝트**가 아니라, 각 구성 요소의 역할과 데이터 흐름을 본인이 설명할 수 있는 프로젝트가 됩니다.

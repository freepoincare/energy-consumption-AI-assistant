# Electricity Consumption AI Assistant

An AI-native web application that analyzes personal electricity consumption time-series data, stores aggregated daily metrics in Firebase Firestore, and provides an intelligent conversational assistant using OpenAI GPT with dynamic context injection and strict anti-hallucination guardrails.

---

## 1. Project Introduction

The Electricity Consumption AI Assistant bridges the gap between raw smart-meter telemetry and human-friendly energy insights. Instead of sending extensive raw measurements to a Large Language Model (which causes context exhaustion, elevated costs, latency, and hallucinations), the backend computes structured, multi-dimensional statistical summaries on the server side. These summaries are dynamically injected into the LLM system prompt for precise, factually grounded answers.

### Architecture Diagram

```mermaid
flowchart TD
    subgraph Client["Frontend Client (Vercel / Static)"]
        UI["Vanilla Dashboard (HTML5 / CSS3 / ES6)"]
        API_JS["API Client (frontend/api.js)"]
        CONFIG_JS["Config (frontend/config.js)"]
    end

    subgraph Backend["FastAPI Backend (Render)"]
        FastAPI_App["FastAPI Engine (app/main.py)"]
        CORS["CORS Middleware"]
        Router_Data["Data Router (/api/data)"]
        Router_Chat["Chat Router (/api/chat)"]
        Router_Conv["Conversations Router (/api/conversations)"]

        Service_Data["EnergyDataService (app/services/data_service.py)"]
        Service_Summary["Summary Engine (app/analysis/summary.py)"]
        Service_AI["AIChatService (app/services/ai_service.py)"]
        Service_Conv["ConversationService (app/services/conversation_service.py)"]
    end

    subgraph Cloud["Cloud Services and Database"]
        Firestore[("Google Cloud Firestore")]
        OpenAI["OpenAI GPT API (gpt-4o-mini)"]
    end

    UI <--> CONFIG_JS
    UI <--> API_JS
    API_JS -->|REST Calls / JSON| CORS
    CORS --> FastAPI_App

    FastAPI_App --> Router_Data
    FastAPI_App --> Router_Chat
    FastAPI_App --> Router_Conv

    Router_Data --> Service_Data
    Service_Data <-->|Read / Write data Collection| Firestore
    Service_Data --> Service_Summary

    Router_Chat --> Service_AI
    Service_AI -->|1. Request Current Stats| Service_Data
    Service_AI -->|2. Injected Prompt + Question| OpenAI
    OpenAI -->|3. Data-Grounded Answer| Service_AI
    Service_AI -->|4. Auto-Persist Thread| Service_Conv
    Service_Conv <-->|Read / Write conversations Collection| Firestore

    Router_Conv --> Service_Conv
```

---

## 2. Problem Statement

Modern smart electricity meters capture consumption at frequent intervals (such as every 30 minutes). However:
- Users struggle to make sense of raw numeric records spanning thousands of rows.
- Directly querying raw records through an LLM causes severe context window exhaustion, high token costs, and hallucinations.
- Energy consumers require concrete answers to questions like: *"What was my highest usage day?"*, *"Do I use more energy on weekends?"*, *"Is my recent trend increasing?"*, and *"What is my estimated cost?"*

This application resolves these challenges via server-side aggregation, structured schema validation, and context-injected AI retrieval.

---

## 3. Why Electricity Consumption Data is Used

Electricity consumption time-series data is an ideal domain for AI-native agentic applications:
1. **Strict Physical Semantics**: Energy units (kWh, kW) and calendar timelines require exactness.
2. **Multi-scale Temporal Patterns**: Patterns exist at daily, day-of-week, weekend vs. weekday, and monthly levels.
3. **Anti-Hallucination Testing**: Verifying whether an AI invents values for specific dates missing from a summary provides a reliable benchmark for production AI safety.

---

## 4. Raw Dataset

The raw dataset contains 30-minute interval readings representing smart-meter recordings:
- **Location**: `data/raw/`
- **Fields**:
  - `timestamp`: UTC ISO datetime string (e.g. `2026-03-01T00:30:00Z`).
  - `consumption_kwh`: Electricity consumed during that exact 30-minute interval.
  - `unit_rate_gbp`: Cost rate applied per kWh.

> [!IMPORTANT]
> **Data Semantics**: The value of `consumption_kwh` in each 30-minute row is **already the energy consumed** in that interval. Daily consumption is computed by **summing** interval values belonging to the same calendar date. Interval values are **not** multiplied by 0.5.

---

## 5. Data Period

- **Start Date**: `2026-03-01`
- **End Date**: `2026-08-31`
- **Total Duration**: 184 consecutive calendar days (6 full months: March through August 2026).
- **Total Records**: 184 daily records aggregated from 8,832 30-minute intervals.

---

## 6. 30-Minute to Daily Aggregation

The aggregation pipeline in [`app/analysis/preprocessor.py`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/app/analysis/preprocessor.py):
1. Parses timestamps and maps them to local calendar dates (`YYYY-MM-DD`).
2. Validates that 48 half-hour intervals exist per calendar day.
3. Computes daily total:
   $$\text{Daily Consumption (kWh)} = \sum_{i=1}^{48} \text{consumption\_kwh}_i$$
4. Saves cleaned records to `data/processed/daily_energy.csv`.

---

## 7. Data Validation

Validation rules implemented in [`app/models/data_models.py`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/app/models/data_models.py):
- **Date Format**: Validated with regex `^\d{4}-\d{2}-\d{2}$` and checked via `datetime.strptime(v, "%Y-%m-%d")` to reject invalid dates like `2026-02-30`.
- **Value**: Must be non-negative (`ge=0.0`).
- **Memo**: Optional text with a maximum of 500 characters.
- **Payload Safety**: Extra fields are stripped or rejected.

---

## 8. Daily Data Model

Pydantic schemas defined in [`app/models/data_models.py`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/app/models/data_models.py):

```python
class DailyEnergyRecord(BaseModel):
    id: str = Field(..., description="Document ID (typically matches date YYYY-MM-DD)")
    date: str = Field(..., description="Calendar date in YYYY-MM-DD format")
    value: float = Field(..., ge=0.0, description="Daily consumption in kWh")
    memo: Optional[str] = Field(default=None, max_length=500)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

---

## 9. Energy Analysis Summary

The summary engine in [`app/analysis/summary.py`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/app/analysis/summary.py) calculates:
1. **Period Metrics**: Start date, end date, and total days (184 days).
2. **Coverage**: 184 complete days (1.0 coverage ratio).
3. **Overall Statistics**: Total consumption (944.32 kWh), daily average (5.13 kWh/day), median, and standard deviation.
4. **Extremes**:
   - Maximum Day: `2026-03-16` (Monday) — 12.21 kWh
   - Minimum Day: `2026-04-11` (Saturday) — 1.44 kWh
5. **Monthly Statistics**: Monthly totals and daily averages (March peak: 232.63 kWh).
6. **Weekday vs Weekend**: Comparative averages and pattern descriptions.
7. **Day-of-Week Averages**: Monday through Sunday breakdown.
8. **Recent Windows**: Rolling 7-day and 30-day averages versus overall average.
9. **Trend Analysis**: Short-term change and long-term linear slope.
10. **Estimated Cost**: Total estimated cost (£246.01), daily average (£1.34/day), and legal disclaimer.

---

## 10. Summary Limitations

While rich in multi-dimensional metrics, the energy summary has architectural boundaries:
- It aggregates statistics for the entire period and specific highlights (extremes, rolling windows).
- It **does not** contain the individual consumption value for arbitrary dates (such as `2026-07-15`) unless that date was an extreme.
- Queries for arbitrary single dates cannot be answered directly from the summary JSON without a direct database query.

---

## 11. Data Flow

### Conceptual Flow

```
Raw 30-minute data
→ preprocessing
→ daily consumption
→ Firestore
→ summary service
→ summary JSON
→ context injection
→ GPT
→ answer
```

### Function Calling Flow (Implemented / Future)

```
GPT
→ tool selection
→ backend validation
→ Firestore
→ tool result
→ GPT
→ answer
```

---

## 12. FastAPI Endpoints

| Category | Method | Path | Description | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| **System** | `GET` | `/health` | Service health status and environment | `200 OK` |
| | `GET` | `/` | Serves dashboard UI or API status | `200 OK` |
| | `GET` | `/docs` | Interactive Swagger UI API documentation | `200 OK` |
| **Data CRUD** | `GET` | `/api/data` | List daily records (supports pagination & sorting) | `200 OK` |
| | `POST` | `/api/data` | Create new daily consumption record | `201 Created` |
| | `GET` | `/api/data/{id}` | Retrieve specific daily record | `200 OK / 404` |
| | `PUT` | `/api/data/{id}` | Update existing daily record | `200 OK / 404` |
| | `DELETE` | `/api/data/{id}` | Delete daily record | `200 OK / 404` |
| **Summary** | `GET` | `/api/data/summary` | Generate aggregated multi-dimensional stats | `200 OK` |
| **AI Chat** | `POST` | `/api/chat` | Context-injected assistant inference | `200 OK` |
| **Conversations**| `GET` | `/api/conversations` | List conversation threads | `200 OK` |
| | `POST` | `/api/conversations` | Create conversation session | `201 Created` |
| | `GET` | `/api/conversations/{id}` | Retrieve full message thread | `200 OK / 404` |
| | `DELETE` | `/api/conversations/{id}`| Delete conversation session | `200 OK / 404` |

---

## 13. Firestore Structure

Two collections are maintained in Google Cloud Firestore:

### 1) Collection: `data`
- **Document ID**: Date string `YYYY-MM-DD` (e.g. `2026-03-01`)
- **Document Fields**:
  - `date`: string (`YYYY-MM-DD`)
  - `value`: number (kWh daily total)
  - `memo`: string (optional user note)
  - `created_at`: string (ISO 8601 timestamp)
  - `updated_at`: string (ISO 8601 timestamp)

### 2) Collection: `conversations`
- **Document ID**: Conversation UUID (e.g. `e8a3d120-7f99-4a92-b5cf-72bca5012345`)
- **Document Fields**:
  - `id`: string (conversation UUID)
  - `title`: string (topic summary or user query)
  - `created_at`: string (ISO 8601 timestamp)
  - `updated_at`: string (ISO 8601 timestamp)
  - `messages`: array of objects:
    - `role`: string (`user` | `assistant` | `system`)
    - `content`: string (message content)
    - `timestamp`: string (ISO 8601 timestamp)

---

## 14. Context Injection

Context injection is implemented in [`app/services/ai_service.py`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/app/services/ai_service.py):
1. Upon receiving `POST /api/chat`, the service invokes `EnergyDataService.get_summary()`.
2. The complete structured summary JSON is embedded into the system prompt.
3. Strict anti-hallucination instructions constrain the model:
   - Rely ONLY on information provided in the summary.
   - Do NOT fabricate numeric values, dates, trends, averages, or costs.
   - Do NOT guess specific days not explicitly present in extremes.
   - Clearly state that data is only available between 2026-03-01 and 2026-08-31.
   - Always use kWh or kWh/day for energy units.
   - Clearly distinguish estimated costs from confirmed utility bills.

---

## 15. Conversation History

- When a chat query is sent to `POST /api/chat`, completed chat exchanges are automatically recorded via `ConversationService.record_chat_exchange()`.
- Conversation sessions are listed via `GET /api/conversations` and ordered chronologically by latest activity.
- Clicking a session loads the complete message history via `GET /api/conversations/{id}`.
- Users can delete unwanted sessions via `DELETE /api/conversations/{id}`.

---

## 16. Frontend

The frontend is built with standard **HTML5, CSS3, and vanilla JavaScript (ES6)**:
- **Structure**:
  - [`frontend/index.html`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/frontend/index.html): Semantic single-page layout (Chat History, AI Chat, Summary Metrics, Daily CRUD Table).
  - [`frontend/style.css`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/frontend/style.css): Responsive design with CSS variables, message bubbles, and loading indicators.
  - [`frontend/config.js`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/frontend/config.js): Runtime client configuration (`window.API_BASE_URL`).
  - [`frontend/api.js`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/frontend/api.js): Centralized REST API client using fetch API with error handling.
  - [`frontend/app.js`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/frontend/app.js): Application logic, DOM events, chat interactions, and CRUD modal handlers.
- **No Framework Overhead**: No React, Vue, Next.js, or build dependencies required.

---

## 17. Environment Variables

| Variable | Description | Example / Default | Required in Production |
| :--- | :--- | :--- | :--- |
| `PORT` | Web server listening port | `8000` (Local) / `10000` (Render) | Yes (set by host) |
| `ENVIRONMENT` | Environment designation | `development` or `production` | Recommended |
| `ALLOWED_ORIGINS` | Comma-separated CORS allowed origins | `https://<your-app>.vercel.app` | **Yes (Backend)** |
| `OPENAI_API_KEY` | OpenAI secret API key | `sk-proj-...` | **Yes (Backend)** |
| `OPENAI_MODEL` | OpenAI completion model | `gpt-4o-mini` | Optional |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Stringified JSON of Google Cloud Service Account | `{"type":"service_account",...}` | **Yes (Render)** |
| `FIREBASE_CREDENTIALS_PATH` | Path to service account file | `serviceAccountKey.json` | Optional (Local) |
| `API_BASE_URL` | Base URL for API requests | `https://<app>.onrender.com` | **Yes (Frontend)** |

> [!CAUTION]
> Never commit `.env` or `serviceAccountKey.json` into source control. All secrets are ignored by `.gitignore`.

---

## 18. Local Setup

### 1) Clone and Virtual Environment
```bash
git clone <repo-url>
cd M1-2
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
```

### 2) Install Dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure Environment
```bash
cp .env.example .env
# Add your OPENAI_API_KEY and Firebase credentials in .env
```

### 4) Run Backend
```bash
uvicorn app.main:app --reload --port 8000
```

- Dashboard UI: `http://localhost:8000/`
- Health Check: `http://localhost:8000/health`
- Swagger Docs: `http://localhost:8000/docs`

---

## 19. Swagger UI

FastAPI automatically generates Open-API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Use Swagger UI to test CRUD endpoints, verify response schemas, and inspect API contracts.

---

## 20. Render Deployment (Backend)

The backend is prepared for [Render](https://render.com) using [`render.yaml`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/render.yaml):
1. Connect repository to Render as a **Web Service**.
2. Configuration:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Environment Variables in Render Dashboard:
   - `OPENAI_API_KEY`: Production OpenAI API key.
   - `OPENAI_MODEL`: `gpt-4o-mini`
   - `FIREBASE_SERVICE_ACCOUNT_JSON`: Complete stringified JSON of your Firebase service account key.
   - `ALLOWED_ORIGINS`: `https://<your-vercel-app>.vercel.app`
   - `ENVIRONMENT`: `production`
4. Verify Render deployment with `GET /health` and `GET /docs`.

---

## 21. Vercel Deployment (Frontend)

The frontend is prepared for [Vercel](https://vercel.com) using [`vercel.json`](file:///C:/Users/skybl/OneDrive/Codyssey/AI_native/projects/M1-2/vercel.json):
1. Import repository into Vercel.
2. Root Directory: `frontend` (or repository root using `vercel.json`).
3. In `frontend/config.js` or deployment configuration, set:
   ```javascript
   window.API_BASE_URL = "https://<your-render-app>.onrender.com";
   ```
4. Deploy and confirm cross-origin requests to Render succeed.

---

## 22. Security Considerations

- **Zero Frontend Secrets**: OpenAI keys and Firebase service account credentials remain exclusively on the backend.
- **CORS Whitelisting**: Strict `ALLOWED_ORIGINS` configuration blocks unauthorized domain requests.
- **Input Validation**: Rigorous Pydantic schema validation for date formats, types, and values.
- **Repository Safety**: `.gitignore` strictly blocks all `.env`, `.json` credentials, and keys.

---

## 23. Estimated-Cost Limitations

- Cost calculations are estimates based on unit rates and interval consumption.
- They do not represent official utility bills, standing charges, taxes, or seasonal tariffs.
- The AI assistant includes explicit disclaimers in all cost discussions.

---

## 24. Function Calling / Tool Use (Implemented)

### Overview & Core Philosophy
The assistant employs **Context Injection by default**: if the pre-computed energy summary contains sufficient information to answer the user's question, GPT answers directly without invoking any tools.

When a query asks for information absent from the summary (e.g., a specific calendar date, a custom date range, or details recorded in a user memo), GPT dynamically invokes internal backend tools via **OpenAI Function Calling**.

### Tools List & Schemas
1. **`get_energy_data_by_date`**:
   - **Description**: Retrieves the actual daily electricity consumption record for a specified date, including `date`, `consumption_kwh`, and `memo`.
   - **Parameters**:
     - `date` (string, required): Date in `YYYY-MM-DD` format (e.g. `2026-07-15`).

2. **`get_energy_data_by_period`**:
   - **Description**: Retrieves daily electricity records for a specified date range (inclusive), returning an array of records with `date`, `consumption_kwh`, and `memo`.
   - **Parameters**:
     - `start_date` (string, required): Range start date in `YYYY-MM-DD` format.
     - `end_date` (string, required): Range end date in `YYYY-MM-DD` format.

3. **`get_energy_statistics`**:
   - **Description**: Calculates aggregate statistics (`total_consumption_kwh`, `average_daily_consumption_kwh`, `minimum`, `maximum`, `records_count`, and memos) for a custom date range.
   - **Parameters**:
     - `start_date` (string, required): Range start date in `YYYY-MM-DD` format.
     - `end_date` (string, required): Range end date in `YYYY-MM-DD format`.

### Complete Tool Execution Flow
```
User Query
  │
  ▼
OpenAI Chat Completion (with tools defined & summary context injected)
  │
  ├─► [Summary Sufficient?] ──► Answer directly from Summary (No Tool Call)
  │
  └─► [Summary Insufficient]
        │
        ▼
      GPT generates tool_call (e.g., get_energy_data_by_date)
        │
        ▼
      Backend Validation Layer
        ├─ Format validation (YYYY-MM-DD)
        ├─ Calendar validity check
        ├─ Dataset boundary check (2026-03-01 to 2026-08-31)
        └─ Period span check (start_date <= end_date, max span)
        │
        ▼
      Service / Repository Layer (Firestore / in-memory fallback)
        │
        ▼
      Tool Result returned as role: "tool" message to GPT
        │
        ▼
      GPT synthesizes final answer grounded in tool data
```

### Security & Architecture Rules
- **No Direct Cloud Access**: GPT never interacts directly with Firestore or credentials. All queries pass through the application service layer.
- **Strict Parameter Validation**: Dates are validated for regex format, valid calendar day, and dataset bounds before querying.
- **Factual Integrity**: Missing records or dates outside the boundary return explicit error notices without fabrication.
- **Whole-Home Consumption Limitation**: The AI Assistant explicitly acknowledges that consumption represents whole-home aggregate electricity, and user memos (e.g., "turned on AC") cannot be claimed as definitive proof of causation. Cautious language is always used:
  - *"This coincides with your note that..."*
  - *"This may be related to..."*
  - *"The whole-home electricity data alone cannot prove that [appliance] caused this change."*

---

## 25. Bonus Features Status

| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Function Calling / Tool Use** | **Implemented** | 3 validated tools (`get_energy_data_by_date`, `get_energy_data_by_period`, `get_energy_statistics`) with context injection priority |
| **Extended Summary Metrics** | **Implemented** | 10+ analytical dimensions in `GET /api/data/summary` (trends, weekday/weekend, day of week, costs) |
| **Interactive Charts** | **Implemented** | Responsive Chart.js daily time-series chart with gradient fills |
| **Data Export** | **Implemented** | CSV export of all daily records (`date`, `consumption_kwh`, `memo`) |
| **Dark Mode** | **Implemented** | Persistent theme toggle stored in `localStorage` |


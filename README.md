# Electricity Consumption AI Assistant

An educational AI-native web application that analyzes personal electricity consumption time-series data, stores aggregated daily insights in Firebase Firestore, and provides an intelligent conversational assistant using OpenAI GPT with dynamic context injection.

---

## 1. Step 1 Mission Summary & Architecture Overview

### Mission Requirements Overview
- **Data Domain**: Personal electricity-consumption time series (30-minute intervals).
- **Core Goal**: Understand user's historical electricity consumption, aggregate it to daily metrics, store in Firestore, and answer natural language user queries via context-injected GPT chatbot.
- **Strict Data Semantics**:
  - `consumption_kwh` in raw data is already the energy consumed during the 30-minute interval.
  - Daily consumption is computed by **summing** interval values belonging to the same local calendar date (do not multiply by 0.5).
  - Estimated cost is an estimation and must not be described as confirmed billing.

### Requirements Breakdown
| Category | Scope |
| :--- | :--- |
| **Mandatory Core Requirements** | - Daily time-series preprocessing & statistical summary generation<br>- FastAPI backend with standard CORS & structured architecture<br>- Firebase Firestore CRUD for `data` and `conversations`<br>- Context Injection Chat endpoint (`POST /api/chat`) with OpenAI GPT<br>- Vanilla HTML/CSS/JS frontend (no heavyweight frameworks)<br>- Deployment to Render (Backend) & Vercel (Frontend) |
| **Optional Bonus Features** | - OpenAI Function Calling / MCP Server integration for dynamic data retrieval<br>- Frontend interactive charts / visualizations & CSV export<br>- Dark mode toggle & extended statistical metrics |

---

## 2. Planned End-to-End Data Flow

```
[Raw 30-min Data: data/raw/energy_raw.csv]
          │
          ▼
[Preprocessing & Validation: app/analysis/preprocessor.py]
  - Validate timestamps & intervals
  - Sum 30-min interval kWh per local calendar day
          │
          ▼
[Daily Energy Dataset: data/processed/daily_energy.csv]
          │
          ▼
[Firestore Database: app/database/firestore.py]
  - Stored in 'data' collection
          │
          ▼
[Analysis / Summary Service: app/analysis/summary.py]
  - Computes period, count, avg/min/max kWh, and trends
          │
          ▼
[Context Injection Engine: app/services/ai_service.py]
  - Injects summary JSON into System Prompt
          │
          ▼
[OpenAI GPT API]  <── (Optional: Tool / Function Calling for specific date queries)
          │
          ▼
[FastAPI Endpoints: app/routers/chat.py]
          │
          ▼
[Vanilla JS Frontend: frontend/]
```

---

## 3. Project Structure

```
M1-2/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entry point & CORS configuration
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # Environment settings & configuration
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── data.py              # Data CRUD & summary endpoints
│   │   ├── chat.py              # AI chatbot endpoints
│   │   └── conversations.py     # Conversation history endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py        # OpenAI interaction & prompt templates
│   │   └── data_service.py      # Business logic for data operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_models.py       # Pydantic schemas for energy data & summaries
│   │   └── chat_models.py       # Pydantic schemas for chat & messages
│   ├── database/
│   │   ├── __init__.py
│   │   └── firestore.py         # Firestore connection & queries
│   └── analysis/
│       ├── __init__.py
│       ├── preprocessor.py      # Raw 30-min aggregation to daily records
│       └── summary.py           # Statistical calculations & trend generation
├── data/
│   ├── raw/                     # Original 30-minute interval CSV data
│   └── processed/               # Cleaned daily aggregated datasets
├── frontend/                    # Vanilla HTML, CSS, and JS frontend
├── tests/                       # Pytest test cases
│   ├── __init__.py
│   └── test_health.py           # Health check endpoint tests
├── .env.example                 # Example environment variable template
├── .gitignore                   # Git ignore configurations
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 4. How to Run Locally

### 1) Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on macOS/Linux
source venv/bin/activate
```

### 2) Install Dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure Environment Variables
```bash
cp .env.example .env
```

### 4) Run the FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Health Check: `http://localhost:8000/health`
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`

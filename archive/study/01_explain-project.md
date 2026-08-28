This project is essentially asking you to build a **small full-stack AI application** where the AI is not just a generic chatbot—it can answer questions using **your own time-series data**.

Since you've already worked with the **Seoul historical temperature dataset**, that would actually fit this mission very well. You could turn your previous temperature-analysis project into the data foundation for this AI assistant.

---

# 1. What is this project actually asking you to build?

Think of the final application as:

> **"My Personal Data AI Assistant"**

For example, if you use your Seoul temperature data, a user could ask:

> **User:** "서울의 여름 기온은 상승하고 있어?"

And your AI could answer:

> **AI:** "네. 분석 결과 서울의 여름 평균기온은 장기적으로 상승하는 추세입니다. 특히 5월과 9월의 상승폭이 크게 나타났습니다."

Or:

> **User:** "35도 이상인 날이 증가하고 있어?"

And the AI answers based on your stored data.

The important point is that **GPT itself doesn't know your dataset**.

Your application has to:

1. Store your data in Firestore.
2. Analyze the data.
3. Create a concise **summary** of the data.
4. Give that summary to GPT as context.
5. GPT uses that context to answer the user's question.
6. Save the conversation.

So the core concept is:

**Your Data → Analysis → Summary → GPT Context → AI Answer**

---

# 2. The big picture

I would divide the project into **5 layers**:

```text
┌─────────────────────────────────────────────┐
│              User / Browser                 │
│                                             │
│   Chat UI │ Data Management │ History       │
└───────────────────┬─────────────────────────┘
                    │ HTTP / JSON
                    ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│                                             │
│  /api/chat                                  │
│  /api/data                                  │
│  /api/data/summary                          │
│  /api/conversations                         │
└──────────────┬──────────────────┬───────────┘
               │                  │
               ▼                  ▼
┌──────────────────────┐   ┌──────────────────┐
│      Firestore       │   │    OpenAI API    │
│                      │   │                  │
│  data                │   │       GPT        │
│  conversations       │   │                  │
└──────────────────────┘   └──────────────────┘
```

And deployment becomes:

```text
                 Internet
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Vercel                Render
     Frontend              Backend
 HTML/CSS/JS              FastAPI
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                Firestore           OpenAI API
```

---

# 3. Your Seoul temperature project could be the data

I think this is one of the most natural ways for you to approach the assignment.

You already have:

```text
date
tavg
tmin
tmax
```

and you've already performed analysis such as:

* long-term temperature trends
* summer temperature trends
* winter temperature trends
* 35°C+ days
* moving averages
* linear regression
* Mann-Kendall
* ARIMA forecasting

You **do not need to put all of your previous analysis into the AI application**.

For this mission, you could simplify it.

For example, Firestore's `data` collection could contain:

```json
{
    "date": "2025-08-15",
    "value": 33.4,
    "memo": "Seoul daily average temperature"
}
```

But there is an important design consideration here.

The assignment specifically describes:

```text
(date, value, memo)
```

So I would follow that interface for the required CRUD functionality.

You could define:

```text
date  → 날짜
value → 대표 온도(tavg)
memo  → "tmin=25.1, tmax=35.2"
```

Or, if you want to make the application more interesting, you could interpret `value` as **daily maximum temperature**, because that allows questions such as:

> "35도 이상인 날이 얼마나 많아?"

However, I'd keep the required schema simple and put more detailed analytical information into the **summary**.

---

# 4. The most important concept: Context Injection

This is probably the **main AI concept** that the assignment wants you to understand.

Suppose Firestore contains:

```text
2025-06-01 → 22.4
2025-06-02 → 24.1
2025-06-03 → 25.3
...
```

You don't want to send thousands of records to GPT every time.

Instead, your backend calculates a summary:

```json
{
    "period": "1907-10 ~ 2026-08",
    "count": 42000,
    "average": 12.8,
    "max": 38.4,
    "min": -19.2,
    "summer_average": 25.1,
    "trend": "increasing",
    "hot_days_35": 125
}
```

Then you construct a system prompt:

```text
You are a Seoul temperature data assistant.

Here is the user's data summary:

Period: 1907-10 ~ 2026-08
Number of records: 42,000
Average temperature: 12.8°C
Maximum temperature: 38.4°C
Minimum temperature: -19.2°C
Summer average: 25.1°C
Long-term trend: increasing
Days above 35°C: 125

Answer the user's questions based on this information.
```

Then:

```text
User:
"서울의 여름 기온은 상승하고 있어?"
```

GPT can answer based on the supplied context.

### This is what the assignment means by:

> **데이터 요약을 시스템 프롬프트에 주입하는 방식(컨텍스트 주입)**

It is **not necessarily RAG**.

You are basically doing:

```text
Database
   ↓
Data Analysis
   ↓
Summary
   ↓
System Prompt
   ↓
GPT
```

That's the heart of the project.

---

# 5. Recommended project structure

I recommend keeping the backend reasonably clean rather than putting everything into `main.py`.

Something like this:

```text
ai-data-assistant/
│
├── backend/
│   │
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── .gitignore
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── data.py
│   │   │   ├── chat.py
│   │   │   └── conversations.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_service.py
│   │   │   ├── summary_service.py
│   │   │   ├── chat_service.py
│   │   │   └── conversation_service.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── data.py
│   │   │   ├── chat.py
│   │   │   └── conversation.py
│   │   │
│   │   └── db/
│   │       ├── __init__.py
│   │       └── firestore.py
│   │
│   └── ...
│
├── frontend/
│   │
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   │
│   ├── js/
│   │   ├── api.js
│   │   ├── chat.js
│   │   ├── data.js
│   │   └── conversations.js
│   │
│   └── ...
│
├── data/
│   └── temperature.csv
│
├── README.md
└── .gitignore
```

You don't *have* to make it this complicated. For an 80-hour educational project, though, this is a good balance between **organization and simplicity**.

---

# 6. What each backend folder does

### `main.py`

The entry point.

```text
main.py
   ↓
create FastAPI app
   ↓
configure CORS
   ↓
register routers
```

For example conceptually:

```python
app.include_router(data.router)
app.include_router(chat.router)
app.include_router(conversations.router)
```

---

### `routers/`

This is the **API layer**.

For example:

```text
routers/data.py

POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}
GET    /api/data/summary
```

The router receives the HTTP request and passes the actual work to a service.

So:

```text
HTTP Request
     ↓
Router
     ↓
Service
     ↓
Firestore
```

---

### `services/`

This is where your **business logic** lives.

For example:

```text
summary_service.py
```

could calculate:

```text
number of records
date range
average
min
max
trend
```

And:

```text
chat_service.py
```

could handle:

```text
get summary
      ↓
create system prompt
      ↓
call OpenAI
      ↓
return response
```

This separation is one of the things the assignment explicitly wants you to be able to explain.

---

# 7. `models/` — Pydantic

Pydantic defines what data your API accepts.

For example:

```python
class DataCreate(BaseModel):
    date: str
    value: float
    memo: str | None = None
```

If someone sends:

```json
{
    "date": "hello",
    "value": "abc"
}
```

your backend can reject it instead of blindly storing invalid data.

So the architecture becomes:

```text
Frontend
   ↓
JSON
   ↓
Pydantic validation
   ↓
Router
   ↓
Service
   ↓
Firestore
```

---

# 8. `db/firestore.py`

This handles your Firebase connection.

Instead of every file doing:

```python
firebase_admin.initialize_app(...)
```

you centralize the database setup.

Conceptually:

```text
Firestore
     ↑
firestore.py
     ↑
services
```

And your Firebase credentials should **never** be committed to GitHub.

---

# 9. Firestore structure

I'd use something like:

```text
Firestore
│
├── data
│    ├── document_001
│    │    ├── date
│    │    ├── value
│    │    └── memo
│    │
│    ├── document_002
│    │    ├── date
│    │    ├── value
│    │    └── memo
│    │
│    └── ...
│
└── conversations
     ├── conversation_001
     │    ├── title
     │    ├── created_at
     │    └── messages
     │
     └── ...
```

For example:

```json
{
    "title": "서울 여름 기온 분석",
    "created_at": "2026-08-28T17:00:00",
    "messages": [
        {
            "role": "user",
            "content": "서울의 여름 기온은 상승하고 있어?"
        },
        {
            "role": "assistant",
            "content": "네, 장기적으로 상승하는 추세입니다."
        }
    ]
}
```

---

# 10. API structure

Your API would look roughly like this:

```text
                    FastAPI
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
     /data           /chat       /conversations
       │               │                │
       ▼               ▼                ▼
    CRUD API       GPT API          History API
```

### Data API

```text
POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}
GET    /api/data/summary
```

### Chat API

```text
POST /api/chat
```

### Conversation API

```text
POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}
```

---

# 11. The most important program flow

Here is the flow I'd recommend you remember.

## A. User asks a question

```text
┌──────────────┐
│    User      │
│              │
│ "여름 기온이 │
│  상승했어?"  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Frontend   │
│  JavaScript  │
└──────┬───────┘
       │
       │ POST /api/chat
       ▼
┌──────────────┐
│   FastAPI    │
│ chat router  │
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│   Chat Service     │
└─────────┬──────────┘
          │
          │ 1. Get summary
          ▼
┌────────────────────┐
│ Firestore / Data   │
└─────────┬──────────┘
          │
          │ 2. Summary
          ▼
┌────────────────────┐
│ Summary Service    │
│                    │
│ avg: 25.1°C        │
│ trend: increasing  │
│ ...                │
└─────────┬──────────┘
          │
          │ 3. Inject context
          ▼
┌────────────────────┐
│   System Prompt    │
│                    │
│ "You are a data    │
│  assistant..."     │
│                    │
│ Data summary: ...  │
└─────────┬──────────┘
          │
          │ 4. API request
          ▼
┌────────────────────┐
│     OpenAI GPT     │
└─────────┬──────────┘
          │
          │ 5. AI answer
          ▼
┌────────────────────┐
│   Chat Service     │
└─────────┬──────────┘
          │
          ├───────────────► Firestore
          │                 save conversation
          │
          ▼
┌────────────────────┐
│      Frontend      │
│                    │
│ "네, 상승하고      │
│  있습니다..."      │
└────────────────────┘
```

That is essentially the **entire project in one diagram**.

---

# 12. Data management flow

When the user adds a temperature record:

```text
User
 │
 │ date/value/memo
 ▼
Frontend
 │
 │ POST /api/data
 ▼
FastAPI
 │
 │ Pydantic validation
 ▼
Data Router
 │
 ▼
Data Service
 │
 ▼
Firestore
 │
 ▼
Success response
 │
 ▼
Frontend updates table
```

For deletion:

```text
User clicks DELETE
       ↓
JavaScript
       ↓
DELETE /api/data/{id}
       ↓
FastAPI
       ↓
Firestore
       ↓
Success
       ↓
Refresh data table
```

---

# 13. Conversation history flow

When the user opens the application:

```text
Frontend
   │
   │ GET /api/conversations
   ▼
FastAPI
   │
   ▼
Firestore
   │
   ▼
Conversation list
   │
   ▼
Frontend
```

Then the user clicks:

> "서울 여름 분석"

```text
Frontend
   │
   │ GET /api/conversations/123
   ▼
FastAPI
   │
   ▼
Firestore
   │
   ▼
messages
   │
   ▼
Frontend
   │
   ▼
Display previous chat
```

---

# 14. What the frontend might look like

You don't need a complicated UI.

I'd make a simple dashboard with **three main areas**:

```text
┌─────────────────────────────────────────────────┐
│       🌡️ Seoul Temperature AI Assistant         │
├─────────────────────────────────────────────────┤
│                                                 │
│  Data Summary                                   │
│  ┌───────────────────────────────────────────┐  │
│  │ Period: 1907–2026                         │  │
│  │ Records: 42,000                           │  │
│  │ Average: 12.8°C                           │  │
│  │ Trend: Increasing                         │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
├───────────────┬─────────────────────────────────┤
│ Conversations │           AI Chat               │
│               │                                 │
│ • Summer      │ User:                           │
│   temperature │ 서울 여름 기온이 상승했어?      │
│               │                                 │
│ • 35°C days   │ AI:                             │
│               │ 네, 장기적으로 상승 추세...     │
│ • Winter      │                                 │
│               │                                 │
│               │ ┌──────────────────────┐        │
│               │ │ 질문을 입력하세요... │ [Send] │
│               │ └──────────────────────┘        │
├───────────────┴─────────────────────────────────┤
│                 Data Management                 │
│                                                 │
│ Date          Value       Memo          Action  │
│ 2025-08-01    29.4        ...           Delete  │
│ 2025-08-02    30.1        ...           Delete  │
└─────────────────────────────────────────────────┘
```

You can make this much prettier later.

---

# 15. What I would NOT do

This is important because you already have quite a sophisticated temperature-analysis project.

I **wouldn't try to put everything you've learned into this application**.

For example, don't start with:

```text
ARIMA
Mann-Kendall
Sen's slope
linear regression
decomposition
35°C analysis
seasonal analysis
forecasting
RAG
vector database
embeddings
MCP
agents
etc.
```

That could turn a manageable 80-hour project into a huge project.

The mission's core is actually much simpler:

```text
Data
 ↓
Firestore
 ↓
Summary
 ↓
Prompt
 ↓
GPT
 ↓
Chat
```

Then:

```text
CRUD
+
Conversation history
+
Frontend
+
Deployment
```

That's enough.

---

# 16. A good scope for YOUR project

Given your existing Seoul temperature work, I would define the project as:

> **서울 기온 데이터를 이해하는 AI 데이터 분석 비서**

The AI could answer questions such as:

```text
"서울의 평균 기온은 얼마야?"

"서울의 여름 기온은 상승하고 있어?"

"가장 더웠던 날은 언제야?"

"35도 이상인 날이 증가하고 있어?"

"최근 10년의 여름 기온은 과거보다 높아?"

"서울의 겨울은 어떻게 변했어?"

"2026년 여름은 어땠어?"
```

However, there is one subtle limitation:

**If you only inject a high-level summary, GPT cannot answer every arbitrary question accurately.**

For example, if the summary only says:

```text
average = 12.8
max = 38.4
trend = increasing
```

then asking:

> "2017년 8월 평균 기온은?"

cannot be answered reliably.

That's actually a useful thing to understand for this project.

The required assignment is teaching you **context injection**, not building a complete analytical agent.

---

# 17. The project can evolve in stages

I recommend this development order:

### Phase 1 — Data

```text
temperature.csv
      ↓
clean/prepare
      ↓
Firestore
```

### Phase 2 — Backend

Build:

```text
FastAPI
  ↓
CRUD
  ↓
Firestore
```

### Phase 3 — Summary

Build:

```text
Firestore data
      ↓
summary_service
      ↓
JSON summary
```

### Phase 4 — AI

Build:

```text
User question
      +
Data summary
      ↓
GPT
      ↓
Answer
```

### Phase 5 — Conversation

Add:

```text
Chat
 ↓
Firestore
 ↓
History
```

### Phase 6 — Frontend

Build:

```text
HTML
CSS
JavaScript
```

### Phase 7 — Deployment

```text
Frontend → Vercel

Backend → Render

Database → Firestore

AI → OpenAI API
```

### Phase 8 — Bonus

Only after everything works:

```text
Graph
CSV export
Dark mode
Function Calling
MCP
```

---

# 18. How the whole system fits together

The final architecture I'd aim for is:

```text
                         USER
                           │
                           ▼
              ┌─────────────────────┐
              │      VERCEL         │
              │                     │
              │ HTML / CSS / JS     │
              │                     │
              │ ┌─────┐ ┌────────┐ │
              │ │ Chat│ │History │ │
              │ └─────┘ └────────┘ │
              │ ┌─────────────────┐ │
              │ │ Data Management │ │
              │ └─────────────────┘ │
              └──────────┬──────────┘
                         │
                    HTTP / JSON
                         │
                         ▼
              ┌─────────────────────┐
              │       RENDER        │
              │                     │
              │      FastAPI        │
              │                     │
              │ ┌─────────────────┐ │
              │ │     Routers     │ │
              │ └────────┬────────┘ │
              │          │          │
              │ ┌────────▼────────┐ │
              │ │    Services     │ │
              │ └──────┬─────┬────┘ │
              └────────┼─────┼──────┘
                       │     │
              ┌────────┘     └─────────┐
              ▼                        ▼
      ┌────────────────┐       ┌────────────────┐
      │   FIRESTORE    │       │   OPENAI API   │
      │                │       │                │
      │ data           │       │      GPT       │
      │ conversations  │       │                │
      └────────────────┘       └────────────────┘
```

And the **AI-specific flow** is:

```text
                   User Question
                         │
                         ▼
                    /api/chat
                         │
                         ▼
                 Get Data Summary
                         │
                         ▼
                ┌─────────────────┐
                │  System Prompt  │
                │                 │
                │ AI instructions │
                │       +         │
                │ Data Summary    │
                └────────┬────────┘
                         │
                         ▼
                     GPT API
                         │
                         ▼
                    AI Answer
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
           User sees it       Save conversation
```

---

## 19. In one sentence

If I had to explain this entire mission to you in the simplest possible way:

> **You are building a web-based personal data assistant where FastAPI manages your data and APIs, Firestore stores the data and conversations, a summary of your data is injected into a GPT system prompt, and a JavaScript frontend lets the user chat with and manage that data.**

And for **your particular case**, I think the strongest project would be to reuse your Seoul temperature dataset rather than starting with a completely new dataset. Your previous analysis gives you a substantial head start, while this project lets you demonstrate a **different skill: turning data analysis into a deployed AI application**.

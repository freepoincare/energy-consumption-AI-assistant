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
       Vercel               Render
      Frontend              Backend
    HTML/CSS/JS             FastAPI
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

최근 LLM의 컨텍스트 창(Context Window)이 수백만 토큰으로 늘어나면서 말씀하신 컨텍스트 인젝션(Context Injection, 단순 프롬프트 입력)이 강력해진 것은 사실입니다. 그럼에도 불구하고 왜 여전히 RAG를 필수적으로 사용하는지, 그리고 컨텍스트 인젝션과의 차이점과 최근 트렌드를 명확하게 정리해 드리겠습니다.

### 1. Context Injection vs RAG 차이점은 무엇인가요?

두 방식 모두 LLM에게 외부 지식을 주고 답변을 유도하는 점은 같지만, "데이터를 언제, 얼마나 집어넣느냐"에서 결정적인 차이가 납니다.

| 비교 항목 | 📥 Context Injection (단순 주입) | 🔍 RAG (검색 기반 증강) |
|---|---|---|
| 작동 방식 | 사용자가 수백 페이지짜리 문서 전체를 프롬프트에 직접 통째로 넣고 질문합니다. | 수만 권의 문서 중 질문에 필요한 핵심 조각(몇 문장/몇 페이지)만 자동으로 찾아내어 프롬프트에 넣어줍니다. |
| 데이터 용량 | LLM의 컨텍스트 창 크기(예: 1M~2M 토큰)로 제한됩니다. | 사실상 무제한 (기가바이트, 테라바이트 급의 기업 데이터 전체 처리 가능). |
| 비용 (API 요금) | 질문할 때마다 전체 문서 비용을 계속 지불해야 하므로 비용이 기하급수적으로 증가합니다. | 찾아낸 핵심 조각(Chunk)의 비용만 내므로 비용이 매우 저렴하고 효율적입니다. |
| 속도 (Latency) | 프롬프트가 너무 길어지면 LLM이 이를 읽고 해석하는 데 수십 초 이상 걸립니다. | 검색 속도가 밀리초(ms) 단위로 빨라 실시간 대화에 유리합니다. |
| 정보 유실 현상 | 문서가 너무 길면 중간에 있는 내용을 AI가 놓치는 "Lost in the Middle" 현상이 발생합니다. | 필요한 핵심만 정확히 짚어서 입력하므로 정확도가 높습니다. |

---

## 2. 요즘에도 RAG를 많이 쓰나요?

네, 과거보다 오히려 훨씬 더 많이, 그리고 깊게 쓰고 있습니다.
성능 좋은 롱컨텍스트(Long-context) 모델(예: Gemini 1.5 Pro)이 등장하면서 *"이제 RAG는 끝났다"*는 이야기가 잠시 나왔으나, 실제 엔터프라이즈(기업용) 환경에서는 비용 효율성과 데이터 관리 이슈 때문에 RAG가 완전히 표준(Standard)으로 자리 잡았습니다.
다만, 요즘의 RAG는 단순 검색에 그치지 않고 Advanced RAG나 AI Agent 기반 RAG 형태로 진화했습니다. 질문을 분석해 검색 키워드를 스스로 재가공하거나, 검색된 결과가 틀렸으면 다시 검색하는 등 훨씬 똑똑한 파이프라인으로 발전했습니다.

---

## 3. RAG는 구체적으로 어떨 때 쓰나요? (핵심 유스케이스)

주로 데이터의 양이 방대하고, 실시간으로 내용이 바뀌며, 비용 통제가 중요할 때 RAG를 도입합니다.

* 기업 내부 문서 검색 가이드 (사내 위키, 매뉴얼): 회사의 수만 개 규정, 제품 설명서, 개발 문서를 다 집어넣고 직원이 질문할 때마다 정확한 규정 링크와 답변을 제공할 때 씁니다.
* 실시간 데이터 반영이 필요할 때: LLM은 과거 데이터만 학습했습니다. 하지만 RAG를 쓰면 오늘 아침에 바뀐 주식 시장 정보나 뉴스 뉴스 기사, 실시간 날씨를 데이터베이스에 넣자마자 AI가 바로 답변에 반영할 수 있습니다.
* 고객센터 AI 챗봇: 고객이 "내 주문 배송 어디쯤 왔어?"라고 물으면, RAG 시스템이 데이터베이스에서 해당 고객의 배송 정보만 쏙 뽑아와서 자연스러운 문장으로 대답해 줍니다.
* 의료/법률/금융 등 전문 도메인: 수천 개의 판례나 의학 논문 중 지금 다루고 있는 사건/환자와 가장 유사한 케이스를 AI가 순식간에 찾아내어 보고서를 작성할 때 활용됩니다.

---

💡 요약하자면:
책 1권 분량의 데이터를 다룰 때는 Context Injection이 편하고 정확할 수 있습니다. 하지만 다뤄야 할 데이터가 수백, 수천 권 분량의 도서관 급이거나 비용을 아끼면서 실시간으로 업데이트해야 한다면 RAG가 유일한 정답입니다.
현재 구상 중이거나 준비하고 계신 서비스의 데이터 용량이나 업데이트 주기는 어느 정도인가요?

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

You don't have to make it this complicated. For an 80-hour educational project, though, this is a good balance between **organization and simplicity**.

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

And your Firebase credentials should never be committed to GitHub.

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

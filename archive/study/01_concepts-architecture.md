# What need to know for this project

Because your goal is to build this **as an AI Native project**, I would not try to learn every technology deeply before starting. You mainly need to understand the **concepts, architecture, and how the pieces connect**, while using AI to help you implement the code.

For this mission, I would organize what you need to know into **10 areas**, roughly in this order.

## 1. Web/API fundamentals ⭐⭐⭐

You need to understand what happens when a frontend talks to a backend.

Learn:

* Client vs. server
* Frontend vs. backend
* HTTP
* Request / response
* JSON
* REST API
* HTTP methods:
  * `GET` → retrieve
  * `POST` → create
  * `PUT` → update
  * `DELETE` → delete
* HTTP status codes:
  * `200`
  * `201`
  * `400`
  * `404`
  * `500`
* Endpoint
* URL / path parameters
* Query parameters
* Request body
* API documentation / Swagger

You should be able to understand:

```text
Frontend
   │
   │ POST /api/data
   │ {"date": "...", "value": 25.3}
   ▼
FastAPI
   │
   ▼
Response
   │
   │ {"id": "abc123", ...}
   ▼
Frontend
```

**You don't need to become a web-development expert.**

---

# 2. CRUD ⭐⭐⭐

This is explicitly required by the mission.

CRUD =

| Letter | Meaning | HTTP   |
| ------ | ------- | ------ |
| C      | Create  | POST   |
| R      | Read    | GET    |
| U      | Update  | PUT    |
| D      | Delete  | DELETE |

For your project:

```text
CREATE
POST /api/data

READ
GET /api/data

UPDATE
PUT /api/data/{id}

DELETE
DELETE /api/data/{id}
```

You should understand the complete flow:

```text
User enters:
2026-08-31
28.5
Hot day

        ↓

POST /api/data

        ↓

FastAPI

        ↓

Firestore

        ↓

Document created

        ↓

Frontend refreshes
```

This is one of the **most important concepts to understand before coding**.

---

# 3. FastAPI ⭐⭐⭐

You need enough FastAPI knowledge to build your backend.

Learn:

### Basic application

```python
from fastapi import FastAPI

app = FastAPI()
```

### Routes

```python
@app.get("/api/data")
def get_data():
    ...
```

### POST

```python
@app.post("/api/data")
def create_data(data: DataCreate):
    ...
```

### Path parameters

```python
@app.get("/api/data/{id}")
def get_data(id: str):
    ...
```

### Request body

Understand:

```text
JSON
 ↓
Pydantic model
 ↓
Python object
```

### Router separation

Understand why:

```text
routers/
    data.py
    chat.py
    conversations.py
```

is better than putting everything into `main.py`.

You don't need to memorize FastAPI syntax. **You should understand what the code is doing.**

---

# 4. Pydantic / Data Validation ⭐⭐

This is another explicit learning objective.

Understand:

> **Pydantic validates incoming data before your application processes it.**

For example:

```python
class DataCreate(BaseModel):
    date: str
    value: float
    memo: str | None = None
```

Then the frontend sends:

```json
{
    "date": "2026-08-31",
    "value": 28.5,
    "memo": "Hot day"
}
```

Pydantic checks whether the data matches the expected structure.

You should understand:

* `BaseModel`
* type hints
* required vs optional fields
* validation
* request schemas
* response schemas

---

# 5. Database / Firestore ⭐⭐⭐

You don't need to become a database engineer.

You need to understand:

### Database

A place where application data is stored.

### Collection

Similar conceptually to a table.

```text
Firestore
│
├── data
│
└── conversations
```

### Document

An individual record.

```text
data
│
├── abc123
│   ├── date
│   ├── value
│   └── memo
│
├── def456
│   ├── date
│   ├── value
│   └── memo
```

You should understand:

* collection
* document
* document ID
* CRUD operations
* querying
* timestamps
* basic Firestore structure

And importantly:

> **Why do we need a database?**

Because your application needs persistent data.

Without it:

```text
Restart server
     ↓
Data disappears
```

With Firestore:

```text
Restart server
     ↓
Data remains
```

---

# 6. Environment Variables & Security ⭐⭐⭐

This is very important for a deployed AI application.

You will have secrets such as:

```text
OPENAI_API_KEY
FIREBASE_SERVICE_ACCOUNT_JSON
```

You should understand:

### ❌ Never

```python
OPENAI_API_KEY = "sk-xxxxxxxx"
```

and push it to GitHub.

### ✅ Instead

```text
.env
```

```text
OPENAI_API_KEY=...
```

and:

```python
os.getenv("OPENAI_API_KEY")
```

Learn:

* `.env`
* `python-dotenv`
* environment variables
* `.gitignore`
* API keys
* secret management

Also understand **why the OpenAI API key must stay on the backend**, rather than being exposed in browser JavaScript.

---

# 7. Frontend JavaScript fundamentals ⭐⭐⭐

Because the assignment specifically says:

> HTML/CSS/JavaScript — no framework

you need some basic JavaScript.

You should know:

### DOM

```javascript
document.getElementById(...)
```

### Events

```javascript
button.addEventListener(...)
```

### Forms

```text
input
 ↓
JavaScript
 ↓
API
```

### `fetch()`

This is particularly important.

```javascript
fetch("/api/data")
```

You need to understand:

```text
JavaScript
    ↓
fetch()
    ↓
HTTP request
    ↓
FastAPI
    ↓
JSON response
    ↓
JavaScript
    ↓
Update HTML
```

You don't need advanced JavaScript.

---

# 8. AI API / LLM fundamentals ⭐⭐⭐

This is the **AI Native part** of the project.

You should understand:

* LLM
* API
* prompt
* system message
* user message
* assistant message
* context
* tokens
* model
* temperature / generation parameters
* API request / response

For this project, especially understand:

```text
System Prompt
+
Data Context
+
User Question
        ↓
       GPT
        ↓
    AI Answer
```

---

# 9. Context Injection ⭐⭐⭐⭐

This is probably the **single most important AI concept in the assignment**.

Suppose your database contains:

```text
42,000 temperature records
```

You don't necessarily send all 42,000 records to GPT.

Instead:

```text
42,000 records
       ↓
Analysis
       ↓
Summary
```

For example:

```text
Period: 1907–2026
Records: 42,000
Average: 12.8°C
Maximum: 38.4°C
Minimum: -19.2°C
Summer average: 25.1°C
Trend: Increasing
```

Then:

```text
System Prompt
       +
Temperature Summary
       +
User Question
       ↓
      GPT
```

You should understand the difference between:

### Generic chatbot

```text
User → GPT
```

and:

### Your application

```text
User
 ↓
Your Backend
 ↓
Your Database
 ↓
Your Data Summary
 ↓
System Prompt
 ↓
GPT
 ↓
Answer
```

That's what makes your application a **data-aware AI assistant**.

---

# 10. Conversation / Chat Architecture ⭐⭐⭐

You also need to understand how a chatbot remembers conversations.

A conversation could be:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "서울 여름 기온이 상승했어?"
    },
    {
      "role": "assistant",
      "content": "네, 상승 추세입니다."
    }
  ]
}
```

Understand:

* conversation
* message
* `role`
* conversation ID
* message history
* saving conversations
* loading conversations
* deleting conversations

And understand that:

> **GPT itself does not automatically give your application permanent conversation storage.**

Your application stores the history in Firestore.

---

# 11. CORS ⭐⭐

This sounds complicated but is actually a relatively small concept.

Your frontend might be:

```text
https://my-app.vercel.app
```

while your backend is:

```text
https://my-api.onrender.com
```

They're different origins.

The browser therefore needs permission to allow:

```text
Vercel
   ↓
Render API
```

That's what CORS controls.

You should understand:

* origin
* CORS
* `allow_origins`
* why CORS matters in production

You don't need deep networking knowledge.

---

# 12. Deployment ⭐⭐

You need to understand the basic idea of deployment.

Locally:

```text
Your computer
├── frontend
└── backend
```

Production:

```text
Internet
   │
   ├── Vercel
   │     └── Frontend
   │
   └── Render
         └── FastAPI
                │
                ├── Firestore
                └── OpenAI
```

Learn:

* Git
* GitHub
* deployment
* environment variables in hosting platforms
* build/start commands
* logs
* CORS in production
* API URLs

You don't need DevOps expertise.

---

# 13. Git/GitHub ⭐⭐

You will need basic Git.

Know:

```bash
git status
git add .
git commit
git push
git pull
```

And understand:

```text
Local project
      ↓
Git
      ↓
GitHub
      ↓
Render / Vercel
```

Also:

```text
.gitignore
```

is particularly important because you don't want:

```text
.env
Firebase credentials
API keys
```

in GitHub.

---

# 14. Data analysis ⭐⭐⭐

Because your project is based on time-series data, you should understand:

* pandas
* datetime
* mean
* min / max
* count
* trend
* aggregation
* rolling average
* basic statistics

For **this particular assignment**, you don't need advanced time-series modeling.

You can probably simplify your existing Seoul project considerably.

For example:

```text
Raw data
   ↓
Clean data
   ↓
Basic statistics
   ↓
Trend
   ↓
Summary
```

You don't need to integrate ARIMA just because you already used it.

---

# 15. JSON ⭐⭐⭐

This is easy but extremely important because JSON is the language connecting your components.

You should be comfortable with:

```json
{
    "date": "2026-08-31",
    "value": 28.5,
    "memo": "Hot day"
}
```

and:

```json
{
    "period": "1907-2026",
    "count": 42000,
    "average": 12.8,
    "trend": "increasing"
}
```

Understand:

```text
Python dictionary
       ↕
      JSON
       ↕
JavaScript object
```

---

# 16. Bonus: Function Calling ⭐⭐⭐⭐

I would **not start here**.

First build:

```text
Context Injection
```

Then learn Function Calling.

The difference is interesting:

### Current required architecture

```text
User
 ↓
Backend gets summary
 ↓
GPT
```

### Function Calling

GPT can decide:

```text
User
 ↓
GPT
 ↓
"I need temperature summary"
 ↓
CALL get_temperature_summary()
 ↓
Backend
 ↓
Firestore
 ↓
Result
 ↓
GPT
 ↓
Answer
```

This makes the AI more **agent-like**.

---

# 17. Bonus: MCP ⭐⭐

Again, don't start here.

MCP is an additional integration layer that can allow an AI client to interact with your application's tools/data.

For this project, think of it as:

```text
GPT / AI Client
       ↓
      MCP
       ↓
Your tools
       ↓
Your API / Database
```

It's interesting for an AI Native portfolio, but it's **not necessary to understand the core application first**.

---

# 18. What you actually need to learn vs. what AI can do for you

This is particularly important for your situation.

### You should understand yourself

```text
⭐⭐⭐⭐
Context injection

⭐⭐⭐
CRUD
FastAPI
Firestore
REST API
JavaScript fetch
OpenAI API
Pydantic
JSON
Environment variables

⭐⭐
CORS
Git/GitHub
Deployment
```

### AI can help you write

```text
FastAPI boilerplate
Pydantic models
Firestore CRUD functions
HTML/CSS
JavaScript
API calls
README
Docker/config files if needed
deployment configuration
error handling
```

But you should still be able to answer:

> "Why is this code here?"

That's much more important than memorizing syntax.

---

# 19. Your learning roadmap

If I were doing this project **as an AI Native learner**, I'd learn it in this order:

```text
                    PROJECT
                       │
                       ▼
              ┌────────────────┐
              │ 1. HTTP / API  │
              └───────┬────────┘
                      ▼
                 2. CRUD
                      │
                      ▼
              ┌───────────────┐
              │ 3. FastAPI    │
              └───────┬───────┘
                      ▼
              4. Pydantic
                      │
                      ▼
              5. Firestore
                      │
                      ▼
             6. Data Summary
                      │
                      ▼
          ┌──────────────────────┐
          │ 7. OpenAI API        │
          │    + Prompt          │
          └──────────┬───────────┘
                     ▼
            8. Context Injection
                     │
                     ▼
           9. Conversation DB
                     │
                     ▼
            10. JavaScript
                     │
                     ▼
              11. CORS
                     │
                     ▼
             12. Deployment
                     │
                     ▼
               13. Bonus
          Function Calling / MCP
```

---

# 20. The "minimum knowledge checklist"

Before starting implementation, I'd make sure you can explain these **15 terms in your own words**:

```text
☐ API
☐ HTTP
☐ GET / POST / PUT / DELETE
☐ CRUD
☐ REST API
☐ JSON
☐ FastAPI
☐ Pydantic
☐ Firestore
☐ Environment variable
☐ CORS
☐ OpenAI API
☐ System prompt
☐ Context injection
☐ Conversation history
```

And you should be able to draw this without looking at the assignment:

```text
                 USER
                   │
                   ▼
              FRONTEND
             HTML/JS/CSS
                   │
                HTTP
                   │
                   ▼
               FASTAPI
                   │
          ┌────────┼─────────┐
          │        │         │
          ▼        ▼         ▼
       Firestore  Summary   OpenAI
          │        │         │
          │        └────┐    │
          │             ▼    │
          │        System    │
          │        Prompt    │
          │             │    │
          │             └────┤
          │                  ▼
          │                 GPT
          │                  │
          └───────┬──────────┘
                  ▼
               RESPONSE
                  │
                  ▼
               FRONTEND
                  │
                  ▼
                 USER
```

**If you understand this diagram, you understand the core of the mission.**

And I would **not spend weeks studying these topics separately before touching the project**. For an AI Native approach, learn each concept just before you implement that part, use AI to generate the initial code, and then make yourself explain and modify the generated code. That will be much more aligned with the purpose of this assignment.

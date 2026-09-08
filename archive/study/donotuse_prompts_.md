# Prompts to Antigravity CLI

I think this is **much better than giving Antigravity one giant prompt**. Since your goal is to learn AI Native development, you want Antigravity to act more like a coding partner whose work you can inspect after every stage.

I would use the following **10-step development process**. Each prompt is designed so that Antigravity **does one stage only**, explains what it changed, and stops before moving to the next stage.

---

## Development roadmap

```text
STEP 1  → Project setup + architecture
STEP 2  → Data preparation + analysis/summary
STEP 3  → FastAPI + Pydantic
STEP 4  → Firestore + Data CRUD
STEP 5  → Data Summary API
STEP 6  → OpenAI Chat + Context Injection
STEP 7  → Conversation History
STEP 8  → Frontend
STEP 9  → Connect frontend + backend
STEP 10 → Deployment + documentation
```

Then, **after the core project works**, you can do:

```text
BONUS 1 → Visualization / CSV / Dark mode
BONUS 2 → Function Calling
BONUS 3 → MCP
```

Below are the prompts I would actually give Antigravity.

---

# STEP 1 — Project setup & architecture

The goal here is **not to build functionality yet**. You want Antigravity to establish a clean foundation.

```text
You are helping me build an educational AI Native project step by step.

The project is an AI data assistant based on Seoul historical daily temperature data.

The final application should:

1. Store time-series data in Firebase Firestore.
2. Provide CRUD APIs through FastAPI.
3. Calculate a summary of the stored data.
4. Inject the summary into an OpenAI GPT system prompt.
5. Provide an AI chat interface.
6. Save and load conversation history.
7. Have a vanilla HTML/CSS/JavaScript frontend.
8. Be deployed with the backend on Render and frontend on Vercel.

IMPORTANT DEVELOPMENT RULE:
We are building this project STEP BY STEP. Do not implement future steps yet.

For STEP 1, only do the following:

1. Inspect the current project directory.
2. Create a clean project structure for:

   * backend
   * frontend
   * data
3. Create the basic FastAPI application.
4. Create a Python virtual-environment setup recommendation.
5. Create requirements.txt with the required packages:

   * fastapi
   * uvicorn
   * firebase-admin
   * openai
   * python-dotenv
6. Create an appropriate .gitignore.
7. Create a .env.example showing the environment variables we will eventually need.
8. Configure the basic FastAPI application and CORS structure, but do not implement the actual APIs yet.
9. Create placeholder folders/files for routers, services, models, and database configuration if appropriate.
10. Create a basic health-check endpoint such as GET /health.
11. Make sure the FastAPI application can run locally.

Do NOT:

* implement Firestore CRUD yet
* implement OpenAI yet
* implement chat yet
* implement conversation history yet
* build the frontend yet
* deploy anything yet

After completing STEP 1:

1. Show me the final directory tree.
2. Explain the purpose of each important file.
3. Explain how to run the FastAPI server locally.
4. Tell me exactly what you implemented.
5. Tell me what remains for STEP 2.
6. Stop and wait for my instruction before making any further changes.
```

**Why this step matters:** you learn what a FastAPI project actually looks like before AI starts generating lots of application logic.

---

# STEP 2 — Data preparation & analysis

Here you bring your **Seoul temperature dataset** into the project.

Since you already have experience with this dataset, this should be relatively easy for you.

```text
Continue the AI Native project from STEP 1.

IMPORTANT:
Only implement STEP 2. Do not implement later steps.

For STEP 2, I want to prepare my Seoul historical daily temperature data for the AI assistant.

My dataset contains Seoul daily temperature data with:

* date
* tavg
* tmin
* tmax

The dataset covers historical Seoul temperatures from approximately 1907 to 2026, with missing observations during the Korean War period.

First inspect the available data files and determine their actual filename, columns, format, and location. Do not assume the filename.

Then:

1. Identify the raw dataset.
2. Create an appropriate processed-data workflow.
3. Validate:

   * date format
   * missing values
   * duplicate dates
   * numeric columns
4. Create useful derived fields if appropriate:

   * year
   * month
   * day_of_year
   * season
5. Create a data-analysis module that can calculate at least:

   * period
   * number of records
   * average temperature
   * minimum temperature
   * maximum temperature
   * recent average
   * basic long-term trend
6. Create a reusable summary function that returns structured Python data suitable for later conversion to JSON.
7. Do not connect this summary to Firestore yet.
8. Do not connect this summary to OpenAI yet.
9. Do not build the frontend yet.

Use pandas where appropriate.

After completing STEP 2:

1. Show me the data-processing flow.
2. Explain every important transformation.
3. Show an example of the generated summary.
4. Explain how this summary will eventually be used by the AI.
5. Tell me what files you created or modified.
6. Stop and wait for my instruction.
```

---

# STEP 3 — FastAPI + Pydantic

Now you build the API layer, but **without Firestore yet**.

This is a good learning step because you can understand API requests and validation separately.

```text
Continue the project from STEP 2.

IMPORTANT:
Only implement STEP 3. Do not implement later steps.

For STEP 3, build the FastAPI API structure and Pydantic request/response models.

Create a clean separation between:

* routers
* services
* models

Implement the Pydantic models needed for the data API, including a model corresponding to:

(date, value, memo)

At minimum, prepare models for:

* creating data
* updating data
* returning data
* returning summary information

Implement the API routes for the required data endpoints:

POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}
GET    /api/data/summary

However, at this stage DO NOT connect them to Firestore.

Use temporary in-memory data or another clearly marked temporary implementation so that I can test the API behavior.

Also:

1. Add appropriate HTTP status codes.
2. Add basic validation.
3. Add reasonable error handling.
4. Make Swagger UI available at /docs.
5. Keep the API logic separate from the router logic.
6. Do not implement OpenAI.
7. Do not implement conversation history.
8. Do not build the frontend.
9. Do not deploy.

After implementation:

1. Explain REST API, CRUD, and Pydantic in terms of this project.
2. Show the endpoint table.
3. Explain one complete request/response example.
4. Tell me how to test the endpoints using Swagger.
5. Tell me which parts are temporary and will be replaced by Firestore in STEP 4.
6. Stop and wait.
```

---

# STEP 4 — Firestore + CRUD

Now replace the temporary storage with the real database.

```text
Continue the project from STEP 3.

IMPORTANT:
Only implement STEP 4. Do not implement later steps.

For STEP 4, connect the FastAPI backend to Firebase Firestore.

Requirements:

1. Configure Firebase Admin SDK.
2. Use environment variables for Firebase credentials.
3. Never hard-code credentials.
4. Create a Firestore collection named:
   data
5. Implement the required CRUD operations:

POST   /api/data
GET    /api/data
PUT    /api/data/{id}
DELETE /api/data/{id}

6. Replace the temporary in-memory implementation from STEP 3 with Firestore.
7. Keep database logic separated from router logic.
8. Use appropriate services/modules.
9. Handle:

   * document not found
   * invalid input
   * database errors
10. Keep the existing Pydantic validation.
11. Do not implement OpenAI yet.
12. Do not implement conversation history yet.
13. Do not build the frontend yet.
14. Do not deploy yet.

After implementation:

1. Explain the Firestore structure.
2. Show an example document.
3. Explain how POST, GET, PUT and DELETE map to Firestore operations.
4. Explain how environment variables protect the Firebase credentials.
5. Explain how to test the CRUD endpoints using Swagger.
6. Tell me what changed compared with STEP 3.
7. Stop and wait.
```

---

# STEP 5 — Data Summary API

This is where your **data analysis project starts becoming an AI application**.

```text
Continue the project from STEP 4.

IMPORTANT:
Only implement STEP 5. Do not implement later steps.

For STEP 5, implement the data summary functionality.

The endpoint is:

GET /api/data/summary

The summary should be generated from the data stored in Firestore.

At minimum, return structured information such as:

* period
* count
* average
* minimum
* maximum
* recent average
* trend

For the Seoul temperature application, also include useful temperature-specific information if it can be calculated reliably, such as:

* summer average
* number of days ≥ 35°C

Keep the summary logic in a dedicated service rather than inside the router.

Important:

1. The summary must be generated from the actual Firestore data.
2. Do not hard-code example values.
3. Return clean JSON.
4. Use a Pydantic response model where appropriate.
5. Handle empty datasets gracefully.
6. Do not implement OpenAI yet.
7. Do not implement conversation history yet.
8. Do not build the frontend yet.

After implementation:

1. Show me an example JSON response using actual data.
2. Explain exactly how the summary is calculated.
3. Explain why we create a summary instead of sending the entire dataset to GPT.
4. Explain how this endpoint will later be used by /api/chat.
5. Stop and wait.
```

---

# STEP 6 — OpenAI Chat + Context Injection ⭐

This is the **core AI step**.

```text
Continue the project from STEP 5.

IMPORTANT:
Only implement STEP 6. Do not implement conversation history or frontend yet.

Now implement the AI chat API.

Create:

POST /api/chat

The request should contain a user's natural-language question.

The chat flow must be:

1. Receive the user's question.
2. Obtain the current data summary from the summary service.
3. Construct a system prompt containing the data summary.
4. Send the system prompt + user question to the OpenAI API.
5. Receive the GPT response.
6. Return the AI response as JSON.

The system prompt should clearly establish that the AI is a data analysis assistant and that it should use the provided Seoul temperature summary when answering.

Important architectural requirement:

Do NOT make the chat router directly contain all of this logic.

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
System Prompt + Summary
↓
OpenAI API
↓
AI Answer

Use the OPENAI_API_KEY environment variable.

Do not expose the API key to frontend JavaScript.

Add reasonable error handling for OpenAI API failures.

Do not implement conversation persistence yet.

Do not build the frontend yet.

After implementation:

1. Show me the request/response format.
2. Show me an example of the generated system prompt using the actual summary structure.
3. Explain "context injection" in simple terms.
4. Explain why the OpenAI API key belongs in the backend.
5. Explain the complete /api/chat flow.
6. Tell me how to test it through Swagger.
7. Stop and wait.
```

---

# STEP 7 — Conversation History

Now the chatbot becomes a persistent application.

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

A conversation should contain information such as:

* conversation ID
* title or name
* created_at
* messages

Each message should contain:

* role
* content

The roles should support at least:

* user
* assistant

Also modify /api/chat so that the completed conversation can be automatically saved according to the mission requirements.

Keep conversation logic in a dedicated conversation service.

Important:

1. Do not expose credentials.
2. Validate request data with Pydantic.
3. Handle missing conversation IDs.
4. Make sure a conversation can be retrieved with its complete message history.
5. Keep the existing data CRUD and summary functionality working.
6. Do not build the frontend yet.
7. Do not deploy yet.

After implementation:

1. Show the Firestore conversation document structure.
2. Explain how a chat becomes a saved conversation.
3. Explain how the frontend will later load an old conversation.
4. Explain what changed in /api/chat.
5. Test the endpoints.
6. Stop and wait.
```

---

# STEP 8 — Frontend

Only now would I ask Antigravity to build the UI.

```text
Continue the project from STEP 7.

IMPORTANT:
Only implement STEP 8. Do not deploy yet.

Build the frontend using ONLY:

* HTML
* CSS
* vanilla JavaScript

Do not use React, Vue, Next.js, or another frontend framework.

Create a clean, modern dashboard for the Seoul Temperature AI Assistant.

The UI should contain three major areas:

1. AI CHAT

* message input
* send button
* conversation display
* loading indicator
* clear distinction between user and AI messages

2. CONVERSATION HISTORY

* list previous conversations
* click a conversation
* load its messages
* display the selected conversation

3. DATA MANAGEMENT

* display current data
* add a data record
* allow at least one CRUD action visibly from the UI
* ideally support add, edit and delete

Also display the current data summary:

* period
* count
* average
* min/max
* trend
* other useful statistics

Create a clean responsive design.

Important:

1. Keep JavaScript separated into sensible files if appropriate.
2. Put API communication in a dedicated JavaScript module where practical.
3. Do not put API keys in the frontend.
4. Use the backend API.
5. Do not hard-code fake AI responses.
6. Do not deploy yet.

At the end:

1. Show me the frontend directory structure.
2. Explain how each UI section communicates with the FastAPI backend.
3. Explain the JavaScript fetch calls.
4. Explain how loading/error states work.
5. Tell me how to run the frontend locally.
6. Stop and wait.
```

---

# STEP 9 — Connect & Test the complete application

This is an important step that I would **not skip**.

```text
Continue the project from STEP 8.

IMPORTANT:
This step is for integration testing and fixing problems only. Do not deploy yet.

Now test the complete application end-to-end.

Verify these flows:

FLOW 1 — Data CRUD

Frontend
→ POST /api/data
→ Firestore
→ frontend refresh

Frontend
→ GET /api/data
→ display data

Frontend
→ PUT /api/data/{id}
→ Firestore
→ frontend refresh

Frontend
→ DELETE /api/data/{id}
→ Firestore
→ frontend refresh

FLOW 2 — Summary

Frontend
→ GET /api/data/summary
→ FastAPI
→ Firestore
→ summary calculation
→ frontend display

FLOW 3 — AI CHAT

Frontend
→ POST /api/chat
→ summary retrieval
→ context injection
→ OpenAI
→ AI response
→ frontend display

FLOW 4 — Conversation history

Chat
→ conversation saved
→ GET /api/conversations
→ conversation list
→ GET /api/conversations/{id}
→ messages displayed

Test for common errors:

* empty input
* invalid data
* nonexistent document
* backend unavailable
* OpenAI API error
* Firestore error
* slow response

Fix only issues that are necessary for the required functionality.

Do not add bonus functionality yet.

After testing:

1. Give me a complete system flow diagram.
2. Give me a list of tested endpoints.
3. Tell me what problems you found and fixed.
4. Tell me what still needs to be done before deployment.
5. Stop and wait.
```

---

# STEP 10 — Deployment + README

Now you have a working application, so deployment becomes much easier.

```text
Continue the project from STEP 9.

IMPORTANT:
This is the deployment and documentation step. Do not add major new functionality.

Prepare the application for production deployment.

BACKEND:

* Deploy FastAPI to Render.
* Make sure the production server starts correctly.
* Configure production environment variables.
* Configure CORS for the Vercel frontend.
* Make sure /docs works on the deployed backend.
* Do not expose secrets.

FRONTEND:

* Prepare the vanilla HTML/CSS/JavaScript frontend for Vercel.
* Configure the production API base URL through an environment/configuration mechanism appropriate for a vanilla frontend deployment.
* Make sure the frontend communicates with the Render backend.

DOCUMENTATION:

Create/update README.md containing:

1. Project introduction
2. Problem statement
3. Main features
4. Architecture
5. Technology stack
6. Directory structure
7. API endpoint table
8. Firestore structure
9. AI context-injection architecture
10. Local installation
11. Environment variables
12. Backend deployment
13. Frontend deployment
14. Swagger URL
15. Limitations
16. Security considerations
17. How conversation history works

Also include a simple architecture diagram in Markdown.

Do not put actual API keys or Firebase credentials in README.

Before finishing:

1. Verify the production URLs.
2. Verify the backend /docs page.
3. Verify the frontend can send a chat.
4. Verify data CRUD works.
5. Verify conversation history works.
6. Verify environment variables are configured correctly.

Finally, give me a deployment checklist and tell me exactly what I should manually verify.

Stop after completing this step.
```

---

# Then: Bonus 1 — Visualization / Export / Dark Mode

Only after the required project is working.

```text
The required AI data assistant is now complete.

Implement the OPTIONAL BONUS features only.

Add:

1. At least one useful temperature visualization.
2. CSV or JSON data export.
3. Dark mode toggle.
4. At least one additional useful statistical metric.

Keep the existing architecture clean.

Do not break:

* CRUD
* summary
* chat
* context injection
* conversation history
* deployment

After implementation, explain each bonus feature and stop.
```

---

# Bonus 2 — Function Calling

This is where the project becomes more genuinely **agent-like**.

```text
The required AI data assistant is complete.

Now implement the OPTIONAL Function Calling bonus.

The goal is to allow GPT to decide when it needs to call an internal application function/tool.

For example, create tools such as:

* get_data_summary
* get_temperature_statistics
* get_conversation

The conceptual flow should be:

User
→ GPT
→ GPT decides whether a tool is needed
→ tool call
→ FastAPI executes the tool
→ result returned to GPT
→ GPT produces final answer

Do not simply hard-code tool calls for every question.

Define clear tool schemas and descriptions so the model can determine when a tool is appropriate.

Log or otherwise make it possible to understand:

* which tool was called
* why it was called
* what result it returned

Update README.md with:

1. Available tools
2. Tool schemas
3. Example tool-call flow
4. Explanation of why a tool was selected

Keep the existing application functionality working.

Do not implement MCP yet.

Stop after completing this bonus.
```

---

# Bonus 3 — MCP

I would leave this until **everything else is finished**.

```text
The AI data assistant and Function Calling implementation are complete.

Now investigate and implement the optional MCP integration required by the mission.

Before changing code:

1. Inspect the existing architecture.
2. Explain where an MCP server fits.
3. Explain the difference between:

   * normal REST API
   * OpenAI Function Calling
   * MCP
4. Propose the smallest MCP implementation that demonstrates the concept without unnecessarily complicating the project.

Then implement the minimum viable MCP integration.

Document:

* MCP server
* available tools
* tool schemas
* client
* request/response flow
* example interaction

Do not rewrite the existing application unnecessarily.

After implementation, provide a simple architecture diagram showing:

AI Client
→ MCP
→ Application tools
→ FastAPI / Firestore

Stop after documentation is complete.
```

---

# One important change I'd make to your original development order

There is one thing I'd emphasize for **your learning**.

Don't think of the project as:

> "I need to finish 10 prompts."

Instead, after **each prompt**, do this:

```text
Antigravity
     ↓
writes code
     ↓
YOU inspect code
     ↓
YOU run it
     ↓
YOU test it
     ↓
YOU ask questions
     ↓
understand
     ↓
NEXT STEP
```

For example, after STEP 3, don't immediately say:

> "Next step."

Instead, ask Antigravity things like:

> "Explain why we separated router and service."

or:

> "Walk me through what happens when POST /api/data is called."

or:

> "Show me the exact path from the frontend request to the Pydantic model."

That will turn the project from **AI-generated code** into an **AI Native learning project**.

---

## Your learning checkpoints

I would especially stop and make sure you understand these points:

| Step      | You should understand                       |
| --------- | ------------------------------------------- |
| **1**     | Project architecture, backend/frontend      |
| **2**     | Data → analysis → summary                   |
| **3**     | API, HTTP, CRUD, Pydantic                   |
| **4**     | Database, Firestore, documents              |
| **5**     | Why create a data summary                   |
| **6** ⭐   | **LLM + system prompt + context injection** |
| **7**     | Conversation persistence                    |
| **8**     | JavaScript + `fetch()` + API                |
| **9**     | Full-stack integration                      |
| **10**    | CORS, environment variables, deployment     |
| **Bonus** | Function Calling / MCP                      |

### And STEP 6 is the one I would spend the most time understanding.

Your final mental model should be:

```text
                  YOUR DATA
                     │
                     ▼
                Firestore
                     │
                     ▼
              Summary Service
                     │
                     ▼
             ┌───────────────┐
             │ Data Summary  │
             └───────┬───────┘
                     │
                     ▼
USER ──────────► FASTAPI
                     │
                     ▼
             SYSTEM PROMPT
             + DATA SUMMARY
             + USER QUESTION
                     │
                     ▼
                   GPT
                     │
                     ▼
                AI ANSWER
                     │
                     ▼
                USER
```

That's the **core AI Native lesson** of this entire mission.

And given your previous Seoul temperature project, this is also a nice progression: **you already know how to analyze the data; this project teaches you how to turn that analysis into a real AI-powered product with an API, database, chatbot, frontend, and deployment.**

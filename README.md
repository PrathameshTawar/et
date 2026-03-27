# EngageTech AI – Social Media Multi-Agent Pipeline

An 8-agent LangGraph pipeline that takes a content brief and produces
platform-optimised, compliance-checked, engagement-scored social media posts
for LinkedIn and Instagram. Wrapped in a production-ready FastAPI backend with
SSE streaming, human-in-the-loop approval, and enterprise RAG via Qdrant.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Agent Pipeline](#agent-pipeline)
3. [Pipeline State](#pipeline-state)
4. [Routing & Control Flow](#routing--control-flow)
5. [FastAPI Backend](#fastapi-backend)
6. [API Reference](#api-reference)
7. [Enterprise Knowledge Base](#enterprise-knowledge-base)
8. [Tech Stack](#tech-stack)
9. [Project Structure](#project-structure)
10. [Installation](#installation)
11. [Environment Variables](#environment-variables)
12. [Running the Server](#running-the-server)
13. [Running the Pipeline Directly](#running-the-pipeline-directly)
14. [Testing](#testing)
15. [Frontend Integration](#frontend-integration)
16. [Streamlit Demo](#streamlit-demo)

---

## Architecture Overview

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph StateGraph                      │
│                                                             │
│  Knowledge → Strategy → Content ──► Compliance             │
│                              ▲           │ approved         │
│                              │           ▼                  │
│                         (retry loop) Engagement             │
│                              │           │ score < 0.65     │
│                              └───────────┘ (max 2 retries)  │
│                                          │ score OK         │
│                                          ▼                  │
│                                    Localization             │
│                                          │                  │
│                                          ▼                  │
│                                      Formatter              │
│                                          │                  │
│                                          ▼                  │
│                                   Human Review ◄── /approve │
│                                          │                  │
│                              publish / edit / reject        │
└─────────────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  AgentCore Memory            Supabase Logs
  (checkpointer)           (engagement_logs table)
```

The **Supervisor** (`agents/Supervisor.py`) owns the `StateGraph` definition,
all routing functions, and the `run_pipeline` entry point. Every agent is a
pure function `(PipelineState) → PipelineState` registered as a LangGraph node.

---

## Agent Pipeline

### 1. Knowledge Agent — `agents/knowledge_agent.py`

Retrieves relevant background context for the query using vector similarity
search against a Qdrant collection (`Knowledge_agent`).

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim vectors)
- Qdrant collection: `Knowledge_agent`, cosine distance
- Returns top-5 matching chunks, joined as `knowledge_context` in state
- Gracefully returns `None` if the collection is empty or the query fails

### 2. Strategy Agent — `agents/strategy_agent.py`

Builds a two-layer content strategy from historical engagement data.

- Fetches the last 50 engagement logs from Supabase (`engagement_logs` table)
- Computes high-performing (score ≥ 0.65) vs low-performing (score ≤ 0.40) signals
- Extracts top hashtags, tones, and topics for each bucket
- Calls **AWS Bedrock Nova-Lite** (`amazon.nova-lite-v1:0`) to generate AI-enhanced
  strategy insights, content ideas, and recommendations on top of the base signals
- Stores `{"base": {...}, "ai": {...}}` in `state["strategy"]`

### 3. Content Creation Agent — `agents/Content_creation.py`

Generates the post caption, image prompt, and hashtags using an LLM.

- LLM: **Groq** `qwen/qwen3-32b` via `langchain-groq`, temperature 0.7
- Injects `knowledge_context`, strategy signals, and memory-based hashtag
  deduplication (avoids repeating hashtags from the last 3 posts)
- Platform-specific instructions: LinkedIn (≤5 hashtags, formal tone) vs
  Instagram (10–30 hashtags, conversational tone)
- Output schema: `ContentCreationOutput(caption, image_prompt, hashtags, platform)`
- Triggers `services/image_generation.py` (AWS Bedrock SDXL) as fire-and-forget
- In the optimization loop, improvement hints from `EngagementAnalysis.improvements`
  are injected into the strategy before regeneration

### 4. Compliance Agent — `agents/compliance_agent.py`

Validates content against safety and platform policy rules.

- LLM: **Groq** `qwen/qwen3-32b`, temperature 0 (deterministic)
- Internal retry loop: up to **5 fix attempts** per invocation
- On `needs_fix`: replaces caption with `corrected_text` and re-evaluates
- On `rejected` or exhausted attempts: exits with final status
- Output: `ComplianceResult(status, reason, corrected_text)`
  - `status` ∈ `{"approved", "rejected", "needs_fix"}`
- Supervisor routes `approved` → Engagement, anything else → END

### 5. Engagement Analysis Agent — `services/Engagement.py`

Predicts engagement potential and drives the optimization loop.

- LLM: **Groq** `qwen/qwen3-32b`, temperature 0, 30s timeout
- Incorporates historical average score from `memory_context` if available
- Output: `EngagementAnalysis(expected_engagement_score, predicted_audience_reaction,
  post_impact_summary, improvements)`
- Threshold: **0.65** — if score < threshold and `optimization_attempts < 2`,
  Supervisor routes back to Content Creation with improvement hints
- Persists result to Supabase `engagement_logs` (best-effort, non-blocking)

### 6. Localization Agent — `agents/localization_agent.py`

Translates and culturally adapts the caption to a target locale.

- LLM: **Groq** `qwen/qwen3-32b`, temperature 0.3
- No-op if `locale` is absent, `"en"`, `"en-us"`, or `"en-gb"`
- Preserves tone, emojis, and intent
- Stores `localized_caption` inside `state["localization"]`

### 7. Formatter Agent — `agents/formatter_agent.py`

Produces platform-specific versions of the final post.

- LLM: **Groq** `qwen/qwen3-32b`, temperature 0.3
- LinkedIn: ≤ 3000 chars, max 5 hashtags, professional tone
- Instagram: ≤ 2200 chars, 10–30 hashtags, conversational tone
- Falls back to simple truncation + hashtag capping if LLM call fails
- Output stored in `state["formatted_posts"]` as:
  ```json
  {
    "linkedin":  {"caption": "...", "hashtags": [...], "image_prompt": "...", "char_count": 412},
    "instagram": {"caption": "...", "hashtags": [...], "image_prompt": "...", "char_count": 890}
  }
  ```

### 8. Human Review Node — `agents/Supervisor.py`

Final gate before publishing.

- CLI mode: prints caption, engagement score, audience reaction, formatted post
  stats, then prompts `publish / edit / no`
- API mode (via `/stream`): emits a `WAITING_HUMAN` SSE event and pauses the
  graph; the frontend calls `POST /api/v1/approve` to inject the decision and
  resume from the LangGraph checkpoint
- `edit` routes back to Content Creation with `edit_instructions` in state
- `publish` / `no` both route to END; `publish` triggers AgentCore persistence

---

## Pipeline State

All agents share a single `PipelineState` TypedDict (`models/state.py`):

| Field | Type | Description |
|---|---|---|
| `query` | `str` | Original content brief |
| `platform` | `str` | `"linkedin"` or `"instagram"` |
| `tasks` | `list[str]` | Reserved for task decomposition |
| `knowledge_context` | `str \| None` | RAG chunks from Qdrant |
| `strategy` | `dict \| None` | `{"base": {...}, "ai": {...}}` |
| `generated_content` | `ContentCreationOutput \| None` | Caption, image prompt, hashtags |
| `optimization_attempts` | `int` | Regeneration counter (max 2) |
| `compliance_result` | `ComplianceResult \| None` | Status + reason |
| `engagement_analysis` | `EngagementAnalysis \| None` | Score + improvements |
| `localization` | `dict \| None` | `{"locale": "es", "localized_caption": "..."}` |
| `formatted_posts` | `dict \| None` | Per-platform formatted output |
| `human_decision` | `str \| None` | `"publish"` / `"edit"` / `"no"` |
| `edit_instructions` | `str \| None` | Free-text edit guidance |
| `memory_context` | `dict \| None` | Loaded from AgentCore / Supabase |

---

## Routing & Control Flow

```
START
  └─► knowledge_agent
        └─► strategy_agent
              └─► content_generation_agent
                    └─► compliance_agent
                          ├─ approved ──► engagement_analysis_agent
                          │                   ├─ score < 0.65 & attempts < 2
                          │                   │       └─► content_generation_agent (loop)
                          │                   └─ score OK ──► localization_agent
                          │                                         └─► formatter_agent
                          │                                               └─► human_review_agent
                          │                                                     ├─ publish ──► END
                          │                                                     ├─ edit ──► content_generation_agent
                          │                                                     └─ no ──► END
                          └─ rejected / needs_fix (exhausted) ──► END
```

Key routing functions in `Supervisor.py`:

- `route_compliance` — approved → engagement, else → END
- `route_engagement` — score < threshold & retries remain → content, else → localization
- `route_human_review` — publish/no → END, edit → content
- `content_node_with_counter` — wraps `content_node` to increment
  `optimization_attempts` and inject improvement hints before each retry

---

## FastAPI Backend

### File Structure

```
backend/
├── main.py                  # App factory, lifespan, CORS, metrics middleware
├── schemas.py               # Pydantic v2 request/response models
├── dependencies.py          # Qdrant client singleton, auth header dependency
├── routers/
│   ├── content.py           # /generate, /stream, /approve
│   └── enterprise.py        # /enterprise/data/upload|list|delete
├── agents/
│   ├── Supervisor.py        # LangGraph graph builder + run_pipeline
│   ├── knowledge_agent.py
│   ├── strategy_agent.py
│   ├── Content_creation.py
│   ├── compliance_agent.py
│   ├── localization_agent.py
│   └── formatter_agent.py
├── services/
│   ├── Engagement.py
│   ├── embedding.py         # SentenceTransformer wrapper
│   ├── image_generation.py  # AWS Bedrock SDXL
│   └── supabase_client.py   # Lazy singleton
├── models/
│   └── state.py             # PipelineState TypedDict
├── tests/
│   ├── test_pipeline.py
│   ├── test_pipeline_state.py
│   ├── test_routing.py
│   ├── test_compliance.py
│   ├── test_content_creation.py
│   └── test_engagement.py
├── requirements.txt
└── .env
```

### Startup Behaviour (`main.py`)

On startup the lifespan handler:
1. Loads `.env` via `python-dotenv`
2. Initialises the async Qdrant client
3. Auto-creates the `enterprise_knowledge` collection if it does not exist
   (384-dim cosine vectors matching `all-MiniLM-L6-v2`)

Every HTTP response carries an `X-Process-Time-Ms` header injected by the
metrics middleware.

### Authentication

All endpoints require the `X-Company-ID` header (demo auth). Missing header
returns `401 Unauthorized`. Replace `verify_company_id` in `dependencies.py`
with real JWT validation for production.

---

## API Reference

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### POST /api/v1/generate

Runs the full 8-agent pipeline synchronously and returns when complete.

Request body:
```json
{
  "query": "Announce our new AI-powered analytics dashboard",
  "platform": "linkedin",
  "locale": "en",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "generated_post": {
    "caption": "Excited to announce...",
    "image_prompt": "A futuristic dashboard...",
    "hashtags": ["#AI", "#Analytics", "#Innovation"],
    "platform": "linkedin",
    "locale": "en"
  },
  "formatted_posts": {
    "linkedin": {"caption": "...", "hashtags": [...], "char_count": 412},
    "instagram": {"caption": "...", "hashtags": [...], "char_count": 890}
  },
  "engagement_score": 0.82,
  "compliance_status": "approved",
  "metrics": {
    "turnaround_seconds": 14.3,
    "consistency_score": 0.97,
    "engagement_improvement": 82.0,
    "knowledge_summary": "Knowledge ingested: 12 documents"
  }
}
```

---

### POST /api/v1/stream

Streams pipeline progress as Server-Sent Events. Pauses at human review.

Request body: same shape as `/generate`.

SSE event types:

| Event | When |
|---|---|
| `start` | Pipeline begins |
| `agent_update` | Each agent completes (`node` field names the agent) |
| `WAITING_HUMAN` | Human review node reached — call `/approve` to continue |

---

## Frontend Integration

A new Next.js 15 frontend is scaffolded under `frontend/` with the following pages:

- `/` : Marketing landing page with 8-agent pipeline hero and features.
- `/dashboard` : Metrics, recent generations, and live pipeline overview.
- `/generate` : Content brief form with SSE stream to `POST http://localhost:8000/api/v1/stream` and live log preview.
- `/knowledge` : Knowledge Base document upload and table.
- `/history` : Past generations table and analytics placeholder.
- `/settings` : Profile, API keys, team, billing sections.

### Run frontend

```bash
cd frontend
npm install
npm run dev
```

Service assumption: backend runs at `http://localhost:8000`. Adjust API host in `app/generate/page.tsx` if needed.


---

## Human-in-the-loop resume endpoint

### POST /api/v1/approve

Request body:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "decision": "publish", 
  "edits": "Make caption more concise"
}
```

Response includes final pipeline metrics and status.

| `complete` | Pipeline finished without human pause |
| `error` | Unhandled exception |

`WAITING_HUMAN` payload:
```json
{
  "session_id": "...",
  "node": "human_review_agent",
  "message": "Awaiting human review. POST /api/v1/approve to continue.",
  "preview": {
    "caption": "Excited to announce...",
    "engagement_score": 0.82
  }
}
```

---

### POST /api/v1/approve

Resumes a paused graph from its LangGraph checkpoint by injecting the human
decision via `graph.update_state(..., as_node="human_review_agent")` then
calling `graph.invoke(None, config=config)`.

Request body:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "decision": "publish",
  "edits": null
}
```

`decision` values: `publish` | `edit` | `reject`  
`edits` is required when `decision = "edit"`.

Response:
```json
{
  "session_id": "...",
  "status": "publish",
  "message": "Post published successfully",
  "metrics": { "turnaround_seconds": 1.2, ... }
}
```

---

## Enterprise Knowledge Base

Documents uploaded via the enterprise endpoints are chunked, embedded, and
stored in the Qdrant `enterprise_knowledge` collection with metadata filtering
by `company_id` and `department`.

### POST /api/v1/enterprise/data/upload

Accepts multipart form data. Indexing runs as a FastAPI `BackgroundTask`.

Supported file types: `PDF`, `TXT`, `CSV`, `DOCX`

Form fields:
- `file` — the document
- `company_id` — company identifier (string)
- `department` — optional department label

Processing pipeline:
1. Extract text (`pypdf` for PDF, `python-docx` for DOCX, UTF-8 decode for TXT/CSV)
2. Sliding-window chunk (512 words, 64-word overlap)
3. Embed with `all-MiniLM-L6-v2` → 384-dim vectors
4. Upsert to Qdrant with payload `{doc_id, chunk_index, text, company_id, department, filename, indexed_at}`

Response (202 Accepted):
```json
{
  "doc_id": "a1b2c3d4-...",
  "filename": "company_policy.pdf",
  "chunk_count": 47,
  "status": "indexed",
  "message": "Indexing 47 chunks in background. doc_id=a1b2c3d4-..."
}
```

### GET /api/v1/enterprise/data/list

Scrolls all Qdrant points and deduplicates by `doc_id`.

Response:
```json
{
  "documents": [
    {
      "doc_id": "a1b2c3d4-...",
      "filename": "company_policy.pdf",
      "company_id": "demo-corp",
      "department": "marketing",
      "chunk_count": 47,
      "indexed_at": "2026-03-23T10:00:00+00:00"
    }
  ],
  "total": 1
}
```

### DELETE /api/v1/enterprise/data/{doc_id}

Removes all Qdrant points whose payload `doc_id` matches. Returns 404 if not found.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph `StateGraph`, LangChain |
| LLM | Groq API — `qwen/qwen3-32b` |
| Strategy LLM | AWS Bedrock — `amazon.nova-lite-v1:0` |
| Image Generation | AWS Bedrock — `stability.stable-diffusion-xl-v1` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, 384-dim) |
| Vector DB (RAG) | Qdrant Cloud (sa-east-1) |
| Engagement Logs | Supabase PostgreSQL (`engagement_logs` table) |
| Long-term Memory | AWS AgentCore `AgentCoreMemorySaver` (checkpointer) |
| API Framework | FastAPI 0.115+, Uvicorn |
| Streaming | Server-Sent Events (SSE) |
| Validation | Pydantic v2 |
| Testing | pytest, hypothesis (property-based) |

---

## Project Structure

```
ET_project/
└── backend/
    ├── main.py
    ├── schemas.py
    ├── dependencies.py
    ├── requirements.txt
    ├── pytest.ini
    ├── .env
    ├── agents/
    │   ├── Supervisor.py
    │   ├── knowledge_agent.py
    │   ├── strategy_agent.py
    │   ├── Content_creation.py
    │   ├── compliance_agent.py
    │   ├── localization_agent.py
    │   ├── formatter_agent.py
    │   └── __init__.py
    ├── routers/
    │   ├── content.py
    │   ├── enterprise.py
    │   └── __init__.py
    ├── services/
    │   ├── Engagement.py
    │   ├── embedding.py
    │   ├── image_generation.py
    │   └── supabase_client.py
    ├── models/
    │   ├── state.py
    │   └── __init__.py
    └── tests/
        ├── test_pipeline.py
        ├── test_pipeline_state.py
        ├── test_routing.py
        ├── test_compliance.py
        ├── test_content_creation.py
        ├── test_engagement.py
        └── __init__.py
```

---

## Installation

```bash
cd ET_project/backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Environment Variables

Create or update `backend/.env`:

```dotenv
# Qdrant Cloud
qdrant_url=https://<your-cluster>.qdrant.io
qdrant_key=<your-qdrant-api-key>

# Groq
GROQ_API_KEY=<your-groq-api-key>

# Supabase
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_KEY=<service-role-key>

# AWS (Bedrock + AgentCore)
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_REGION=us-east-1

# AgentCore memory checkpointer
AGENTCORE_MEMORY_ID=<your-memory-id>
```

The test suite runs with dummy values for all keys. Only live pipeline
execution requires valid credentials.

PowerShell quick-set:
```powershell
$env:GROQ_API_KEY        = "gsk_..."
$env:AGENTCORE_MEMORY_ID = "mem_..."
$env:SUPABASE_URL        = "https://xxxx.supabase.co"
$env:SUPABASE_KEY        = "eyJ..."
$env:AWS_REGION          = "us-east-1"
```

---

## Running the Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- OpenAPI UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

---

## Running the Pipeline Directly

```python
from agents.Supervisor import run_pipeline

state = run_pipeline(
    query="AI in healthcare and its future impact",
    platform="linkedin",
    locale="en",
)

print("Caption:", state["generated_content"].caption)
print("Engagement:", state["engagement_analysis"].expected_engagement_score)
print("Formatted:", state["formatted_posts"])
```

The `human_review_node` will prompt the console for `publish / edit / no`.
On `publish`, the final state is persisted to AgentCore memory automatically.

---

## Testing

```bash
cd backend
pytest
```

The test suite covers:
- `test_pipeline_state.py` — PipelineState field validation and defaults
- `test_routing.py` — Supervisor routing functions (compliance, engagement, human review)
- `test_compliance.py` — ComplianceResult schema and fix-loop edge cases
- `test_content_creation.py` — ContentCreationOutput invariants
- `test_engagement.py` — EngagementAnalysis score bounds and improvement list
- `test_pipeline.py` — End-to-end pipeline integration with mocked LLM calls

Property-based tests use `hypothesis` to verify invariants across random inputs.

---

## Frontend Integration

### 1. Synchronous generation

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-Company-ID: demo-corp" \
  -d '{
    "query": "Launch our new AI dashboard",
    "platform": "linkedin",
    "locale": "en"
  }'
```

### 2. SSE streaming (JavaScript)

```js
const res = await fetch("http://localhost:8000/api/v1/stream", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-Company-ID": "demo-corp",
  },
  body: JSON.stringify({
    query: "Sustainability campaign",
    platform: "instagram",
  }),
});

const reader = res.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  // Parse SSE lines
  for (const line of text.split("\n")) {
    if (line.startsWith("data:")) {
      const data = JSON.parse(line.slice(5));
      if (data.node === "WAITING_HUMAN") {
        // Store session_id and show approval UI
        sessionStorage.setItem("session_id", data.session_id);
      }
    }
  }
}
```

### 3. Human-in-the-loop approval

```bash
curl -X POST http://localhost:8000/api/v1/approve \
  -H "Content-Type: application/json" \
  -H "X-Company-ID: demo-corp" \
  -d '{
    "session_id": "<uuid-from-stream>",
    "decision": "publish"
  }'
```

With edit instructions:
```bash
curl -X POST http://localhost:8000/api/v1/approve \
  -H "Content-Type: application/json" \
  -H "X-Company-ID: demo-corp" \
  -d '{
    "session_id": "<uuid-from-stream>",
    "decision": "edit",
    "edits": "Make the tone more casual and add a call-to-action"
  }'
```

### 4. Upload enterprise document

```bash
curl -X POST http://localhost:8000/api/v1/enterprise/data/upload \
  -H "X-Company-ID: demo-corp" \
  -F "file=@company_policy.pdf;type=application/pdf" \
  -F "company_id=demo-corp" \
  -F "department=marketing"
```

### 5. List and delete documents

```bash
# List
curl http://localhost:8000/api/v1/enterprise/data/list \
  -H "X-Company-ID: demo-corp"

# Delete
curl -X DELETE http://localhost:8000/api/v1/enterprise/data/<doc_id> \
  -H "X-Company-ID: demo-corp"
```

---

## Streamlit Demo

Install extra dependency:
```bash
pip install sseclient-py streamlit
```

```python
import streamlit as st
import requests
import json
import sseclient

API = "http://localhost:8000/api/v1"
HEADERS = {"X-Company-ID": "demo-corp"}

st.set_page_config(page_title="EngageTech AI", layout="wide")
st.title("EngageTech AI Content Pipeline")

col1, col2 = st.columns(2)
with col1:
    query = st.text_area("Content brief", height=100,
                         placeholder="e.g. Announce our new AI analytics dashboard")
with col2:
    platform = st.selectbox("Platform", ["linkedin", "instagram"])
    locale = st.text_input("Locale (optional)", value="en")

if st.button("Generate (stream)", type="primary"):
    payload = {"query": query, "platform": platform, "locale": locale}
    progress = st.empty()
    agents_done = []

    with requests.post(f"{API}/stream", json=payload,
                       headers=HEADERS, stream=True) as r:
        client = sseclient.SSEClient(r)
        for event in client.events():
            data = json.loads(event.data)

            if event.event == "agent_update":
                agents_done.append(data["node"])
                progress.info(f"Completed: {' → '.join(agents_done)}")

            elif event.event == "WAITING_HUMAN":
                st.session_state["session_id"] = data["session_id"]
                st.session_state["preview"] = data.get("preview", {})
                progress.empty()
                st.warning("Human review required")
                st.json(data["preview"])
                break

            elif event.event == "complete":
                progress.success("Pipeline complete")
                st.json(data.get("metrics", {}))
                break

            elif event.event == "error":
                st.error(data.get("detail", "Unknown error"))
                break

if "session_id" in st.session_state:
    st.divider()
    st.subheader("Review & Approve")
    st.json(st.session_state.get("preview", {}))

    decision = st.radio("Decision", ["publish", "edit", "reject"],
                        horizontal=True)
    edits = None
    if decision == "edit":
        edits = st.text_area("Edit instructions")

    if st.button("Submit decision"):
        resp = requests.post(
            f"{API}/approve",
            json={
                "session_id": st.session_state["session_id"],
                "decision": decision,
                "edits": edits,
            },
            headers=HEADERS,
        )
        result = resp.json()
        st.success(result["message"])
        st.json(result["metrics"])
        del st.session_state["session_id"]
```

Run with:
```bash
streamlit run streamlit_demo.py

uvicorn main:app --reload --port 8000

```

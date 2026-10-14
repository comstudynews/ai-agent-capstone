# AI Agent Capstone — Cookbook

A standalone, fictional IT operations agent tutorial. All data and code are newly written and do not contain private institution, instructor or business information.

## Learning tracks

- **Track A (offline, verified):** Python 3.11+ to 3.13, FastAPI, SQLite, deterministic Agent, MCP-like contracts, SSE, evaluation, routing, planning. No API key required.
- **Track B (external integrations, not environment-verified):** actual stdio MCP server, LangChain / LangGraph with an LLM, Qdrant semantic search, PostgreSQL Checkpointer and Next.js frontend. These require packages and services described below.

**Important:** Deterministic Track A teaches system boundaries but is **not itself an LLM or MCP-protocol integration**. For the latter, complete Track B and its verification commands.

## Quick start

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -e . pytest ruff
cp .env.example .env  # Windows: copy .env.example .env
python scripts/check_env.py
pytest -q
uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

Test `/health` at http://127.0.0.1:8000/health. To see streaming:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"payment-api 500 장애 상태"}'
```

Frontend (requires npm registry/network): `cd frontend && npm install && npm run dev`.

## Actual MCP and LLM track

```bash
pip install -e '.[agent,rag,persistence]' pytest ruff
python -m app.mcp_server       # stdio: typically silent while waiting
python -m app.mcp_client       # separate terminal: protocol round trip
```

Configure `AGENT_MODE=llm`, `OPENAI_API_KEY`, `OPENAI_MODEL` with a model you can access. The MCP server must use the pinned, compatible SDK v1 family. For Qdrant, index fictional documents with `python scripts/index_rag.py`, then set `SEARCH_MODE=qdrant`; using a Qdrant collection also requires adapting MCP manual Tool to call `app.rag.retrieve`. For Postgres, set `CHECKPOINT_MODE=postgres` and a real `DATABASE_URL`.

## The 15 recipes

Each recipe has an executable checkpoint `python -m app.lesson N` and a dedicated explanation under `steps/stepNN/README.md`. The checkpoints are **not** complete independent copies of the entire application; the common `app/` and `frontend/` directories cumulatively implement the service. MCP, LLM, Qdrant, Postgres, and frontend tracks require their own real service tests.

## Write-operation safety

The chat Agent does not receive a ticket-creation Tool. In local demo mode a protected `POST /tickets/approve` endpoint requires a private `X-Demo-Admin-Key` that the student sets in `.env`; this is a controlled training exercise, **not production authentication**. Do not expose the demo API to the public internet. Never place that key in Next.js public environment variables.

## Verification status

- The offline unit/API tests run with no network and validate contracts, SQLite idempotency, routing, streaming, approvals and demo evaluation.
- Actual MCP/LLM/VectorDB/PostgreSQL/Next.js builds require external packages/services. Source is provided for study, but those integrations must be verified in the target environment before public production use.
- Package version ranges are **candidates**, not a proven lockfile. The runtime must be pinned after live compatibility tests.

See `docs/VALIDATION.md`, `docs/ARCHITECTURE.md`, and each recipe page.

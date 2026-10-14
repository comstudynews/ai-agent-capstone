# Verification matrix

## Offline automated checks

```bash
python -m pytest -q
python -m compileall -q app tests scripts
python -m app.lesson 1
python -m app.lesson 15
```

These tests cover SQLite persistence, idempotent ticket creation, Thread isolation, return contracts, routing, Dynamic Planning, SSE frames and arbitrary chunk splits, FastAPI health/chat/stream, approval guard, all lesson entrypoints.

## External integration checks — run on a connected workstation

1. With the `agent` extra installed, `python -m app.mcp_client` lists tools, reads a Resource and Prompt, and invokes the monitoring Tool over **real stdio**. Repeat with Inspector.
2. With LLM API credentials set, `AGENT_MODE=llm` and a valid model name, launch FastAPI, send a read-only question and confirm an actual MCP Tool invocation.
3. With Qdrant available and the `rag` extra installed, run `python scripts/index_rag.py`, switch `SEARCH_MODE=qdrant`, verify retrieved source IDs, then connect `app.rag.retrieve` to the MCP search Tool.
4. With PostgreSQL available, set `CHECKPOINT_MODE=postgres`, restart FastAPI, and confirm same-Thread history plus authorization strategy.
5. In the frontend, run `npm install && npm run build && npm run dev`, ask a question, stop an in-progress stream and inspect state events. A minimal `useChat` UI Message Stream v1 adapter exists at `/chat/ui-stream` with backend protocol tests; verify the full npm build and browser behavior.
6. Verify sensitive strings do not occur in code, docs, sample data, or UI. Do not upload real API keys or organization data.

**Be precise:** a passed offline suite is not proof that all optional integrations work together. Pin packages and record outputs only after each end-to-end test.

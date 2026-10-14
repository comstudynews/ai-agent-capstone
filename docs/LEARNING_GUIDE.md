# How to learn with this cookbook

Before each recipe, answer four questions: **What problem does this solve? Why is this tool or pattern chosen? Which file changes? How do we verify?** The small offline checkpoint provides an observable result before larger service integration.

## Scaffold for beginners

1. **Understand:** read only the chapter's key concept and one comparison table.
2. **Try a tiny result:** run `python -m app.lesson N`; explain what appeared and why.
3. **Inspect code:** open the file listed in the recipe; identify the function and its inputs/outputs.
4. **Connect:** run the test or API check; verify the same result on the service boundary.
5. **Extend:** change one mock value; predict and compare the output.
6. **Debug:** trace data from source → Tool → Agent → API → Browser, stopping at the first changed value.

Avoid re-explaining Tool vs Resource, SSE vs Agent Stream, or Checkpointer in later chapters; refer back to their first occurrence. New chapters should emphasize what's *different* from the previous stage.

## Complexity ladder

| Stage | Tiny test | Bigger integration |
| --- | --- | --- |
| MCP | Identify 6 capabilities | Real stdio Client/Server |
| API | `/health` | LangChain Agent and RAG |
| SSE | Parse one event | Browser with full stream lifetime |
| Observability | Deterministic evaluator | Trace/Spans with configured LangSmith |
| State | SQLite demo history | PostgreSQL LangGraph Checkpointer |
| Routing | Rule-based route | Tool-connected Graph |
| Planning | Bounded demo plan | Condition-driven retries and Tool calls |

If an optional service is unavailable, the offline checkpoint still teaches the interface; **never present the offline simulation as a completed MCP/LLM integration**.

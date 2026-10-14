"""실제 Qdrant/PostgreSQL을 사용하는 선택형 통합 테스트.

INTEGRATION_SERVICES=1 환경에서만 실행하며, 외부 LLM API Key는 필요하지 않습니다.
"""
import asyncio
import os
import uuid
from typing import TypedDict

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("INTEGRATION_SERVICES") != "1",
    reason="실제 로컬 DB 연동은 INTEGRATION_SERVICES=1에서 실행",
)


def test_real_qdrant_uses_relevance_scores(monkeypatch):
    from langchain_core.embeddings import Embeddings
    from langchain_openai import OpenAIEmbeddings
    from app import rag

    class DemoEmbeddings(Embeddings):
        def __init__(self, model=None):
            self.model = model

        def embed_documents(self, texts):
            return [self.embed_query(text) for text in texts]

        def embed_query(self, text):
            lowered = text.lower()
            vector = [
                float("api" in lowered),
                float("500" in lowered),
                float("db" in lowered),
                float("지연" in lowered),
                1.0,
            ]
            norm = sum(v * v for v in vector) ** 0.5
            return [v / norm for v in vector]

    monkeypatch.setattr("langchain_openai.OpenAIEmbeddings", DemoEmbeddings)
    monkeypatch.setenv("SEARCH_MODE", "qdrant")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    assert rag.index_demo_documents() == 3
    hits = rag.retrieve("API 500")
    assert hits
    assert all(0.0 <= hit["score"] <= 1.0 for hit in hits)
    assert all(hit["source"].startswith("qdrant://") for hit in hits)


def test_postgres_checkpoint_survives_context_restart(monkeypatch):
    monkeypatch.setenv("CHECKPOINT_MODE", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://demo:demo@localhost:5432/agentdb")
    from langgraph.graph import END, START, StateGraph
    from app.checkpoint import checkpointer_context

    class CountState(TypedDict):
        count: int

    def build(checkpointer):
        builder = StateGraph(CountState)
        builder.add_node("increment", lambda state: {"count": state["count"] + 1})
        builder.add_edge(START, "increment")
        builder.add_edge("increment", END)
        return builder.compile(checkpointer=checkpointer)

    async def scenario():
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        async with checkpointer_context() as saver:
            graph = build(saver)
            result = await graph.ainvoke({"count": 5}, config=config)
            assert result["count"] == 6
        async with checkpointer_context() as saver:
            graph = build(saver)
            saved = await graph.aget_state(config)
            assert saved.values["count"] == 6

    asyncio.run(scenario())

"""이전 목 기반 검증에서 재현된 회귀 문제를 검사합니다."""
from types import SimpleNamespace
import sys

import pytest
from fastapi.testclient import TestClient

from app.api import app
from app.approval import create_approved_ticket, issue_approval_token
from app.core import process, route
from app.store import IdempotencyConflictError, create_ticket, search_tickets


def test_ticket_status_not_routed_to_incident():
    assert route("티켓 상태 알려줘") == "ticket"
    assert process("티켓 상태 알려줘", "ticket-status")["route"] == "ticket"


def test_monitoring_uses_requested_service():
    result = process("inventory-api 상태 확인", "inventory")
    assert result["route"] == "incident"
    assert result["evidence"][0]["service"] == "inventory-api"
    assert "inventory-api 상태는 OK" in result["answer"]
    assert "payment-api" not in result["answer"]


def test_missing_service_never_defaults_to_payment():
    result = process("서비스 상태 알려주세요", "missing-service")
    assert "서비스명을 알려주세요" in result["answer"]
    assert not result["evidence"]


def test_unknown_service_keeps_not_found():
    result = process("unknown-api 상태 확인", "unknown-service")
    assert "unknown-api" in result["answer"]
    assert "찾을 수 없습니다" in result["answer"]
    assert not result["evidence"]


def test_follow_up_uses_previous_service_and_keeps_other_threads_isolated():
    first = process("search-api 상태 확인", "conversation-1")
    second = process("그 서비스 상태는?", "conversation-1")
    separate = process("그 서비스 상태는?", "conversation-2")
    assert first["evidence"][0]["service"] == "search-api"
    assert second["evidence"][0]["service"] == "search-api"
    assert "이전 질문" in second["answer"]
    assert "서비스명을 알려주세요" in separate["answer"]


def test_idempotency_key_identical_retry():
    first = create_ticket("Demo API issue", "Repeated errors detected", "req-key-001")
    second = create_ticket("Demo API issue", "Repeated errors detected", "req-key-001")
    assert first["created"] is True
    assert second["created"] is False
    assert len(search_tickets("Demo")) == 1


def test_idempotency_key_content_conflict():
    create_ticket("Demo API issue", "Repeated errors detected", "req-key-002")
    with pytest.raises(IdempotencyConflictError):
        create_ticket("Different title", "Different description", "req-key-002")
    assert len(search_tickets("")) == 1


def test_unsigned_and_tampered_mcp_write_refused(monkeypatch):
    monkeypatch.setenv("DEMO_ADMIN_KEY", "test-secret-only-for-local-tests-123")
    args = ("Demo API issue", "Repeated errors detected", "req-key-003")
    with pytest.raises(PermissionError):
        create_approved_ticket(*args, "")
    token = issue_approval_token(*args)
    with pytest.raises(PermissionError):
        create_approved_ticket("Different title", args[1], args[2], token)
    with pytest.raises(PermissionError):
        create_approved_ticket(*args, token + "invalid")
    assert create_approved_ticket(*args, token)["created"] is True
    assert create_approved_ticket(*args, token)["created"] is False


def test_mcp_write_requires_explicit_signing_secret(monkeypatch):
    monkeypatch.delenv("DEMO_ADMIN_KEY", raising=False)
    monkeypatch.delenv("MCP_APPROVAL_SIGNING_KEY", raising=False)
    with pytest.raises(PermissionError):
        issue_approval_token("Demo API issue", "Repeated errors", "req-key-004")


def test_http_api_returns_409_for_changed_idempotent_request(monkeypatch):
    monkeypatch.setenv("DEMO_ADMIN_KEY", "test-secret-only-for-local-tests-123")
    data = {"title": "Demo API issue", "description": "Repeated errors detected",
            "request_id": "req-key-005"}
    with TestClient(app) as client:
        header = {"X-Demo-Admin-Key": "test-secret-only-for-local-tests-123"}
        assert client.post("/tickets/approve", json=data).status_code == 403
        first = client.post("/tickets/approve", json=data, headers=header)
        assert first.status_code == 200 and first.json()["created"] is True
        conflict = client.post("/tickets/approve",
                               json={**data, "description": "A different problem"},
                               headers=header)
        assert conflict.status_code == 409
        assert conflict.json()["detail"]["code"] == "IDEMPOTENCY_CONFLICT"


def test_qdrant_provides_measured_relevance(monkeypatch):
    from app import rag
    fake_doc = SimpleNamespace(metadata={"source_id": "DOC-42", "title": "Manual"},
                               page_content="Fictional instructions")
    class Embeddings:
        def __init__(self, **kwargs):
            pass
    class Store:
        @staticmethod
        def from_existing_collection(**kwargs):
            return SimpleNamespace(
                similarity_search_with_relevance_scores=lambda keyword, k: [(fake_doc, 0.42)]
            )
    monkeypatch.setenv("SEARCH_MODE", "qdrant")
    monkeypatch.setenv("QDRANT_URL", "http://invalid.local:6333")
    monkeypatch.setitem(sys.modules, "langchain_openai",
                        SimpleNamespace(OpenAIEmbeddings=Embeddings))
    monkeypatch.setitem(sys.modules, "langchain_qdrant",
                        SimpleNamespace(QdrantVectorStore=Store))
    results = rag.retrieve("example")
    assert len(results) == 1 and results[0]["score"] == pytest.approx(0.42)
    assert results[0]["source"] == "qdrant://DOC-42"


def test_qdrant_rejects_non_normalized_scores(monkeypatch):
    from app import rag
    fake_doc = SimpleNamespace(metadata={}, page_content="some text")
    class Store:
        @staticmethod
        def from_existing_collection(**kwargs):
            return SimpleNamespace(
                similarity_search_with_relevance_scores=lambda keyword, k: [(fake_doc, 1.5)]
            )
    monkeypatch.setenv("SEARCH_MODE", "qdrant")
    monkeypatch.setenv("QDRANT_URL", "http://invalid.local:6333")
    monkeypatch.setitem(sys.modules, "langchain_openai",
                        SimpleNamespace(OpenAIEmbeddings=lambda **kwargs: object()))
    monkeypatch.setitem(sys.modules, "langchain_qdrant",
                        SimpleNamespace(QdrantVectorStore=Store))
    with pytest.raises(ValueError, match="유사도"):
        rag.retrieve("example")

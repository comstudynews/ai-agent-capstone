from fastapi.testclient import TestClient
from app.api import app


def test_health_and_chat():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        x = client.post("/chat", json={"message": "payment-api 상태", "thread_id": "test"})
        assert x.status_code == 200 and x.json()["thread_id"] == "test"


def test_stream_and_end_marker():
    with TestClient(app) as client:
        response = client.post("/chat/stream", json={"message": "payment-api 상태"})
        assert response.status_code == 200
        assert "event: start" in response.text
        assert "event: state" in response.text
        assert "event: token" in response.text
        assert "event: done" in response.text


def test_approval_requires_key(monkeypatch):
    payload = {"title": "API error 500", "description": "Repeated 500 response", "request_id": "request-123"}
    with TestClient(app) as client:
        assert client.post("/tickets/approve", json=payload).status_code in {403, 503}
        monkeypatch.setenv("DEMO_ADMIN_KEY", "superlong-private-demo-key")
        r = client.post("/tickets/approve", json=payload,
                        headers={"X-Demo-Admin-Key": "superlong-private-demo-key"})
        assert r.status_code == 200 and r.json()["created"]
        again = client.post("/tickets/approve", json=payload,
                            headers={"X-Demo-Admin-Key": "superlong-private-demo-key"})
        assert not again.json()["created"]

import json
from fastapi.testclient import TestClient
from app.api import app
from app.ui_protocol import ui_frame, ui_done


def test_ui_frames():
    assert ui_frame({"type": "text-start", "id": "a"}).startswith('data: {"type":"text-start"')
    assert ui_done() == "data: [DONE]\n\n"


def test_ui_stream_validates_input_and_finishes():
    with TestClient(app) as client:
        invalid = client.post("/chat/ui-stream", json={"messages": []})
        assert invalid.status_code == 422
        r = client.post("/chat/ui-stream", json={"id": "test-ui", "messages": [
            {"role": "user", "parts": [{"type": "text", "text": "payment-api 500 상태"}]}
        ]})
        assert r.status_code == 200
        assert r.headers["x-vercel-ai-ui-message-stream"] == "v1"
        body = r.text
        assert '"type":"start"' in body
        assert '"type":"text-start"' in body
        assert '"type":"text-delta"' in body
        assert '"type":"text-end"' in body
        assert '"type":"finish"' in body
        assert body.endswith("data: [DONE]\n\n")

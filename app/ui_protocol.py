"""UI Message Stream v1 frame builder for Vercel AI SDK transport.

This is a different protocol from our tutorial's custom `event: token` SSE.
"""
import json


def ui_frame(payload: dict) -> str:
    return "data: " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n\n"


def ui_done() -> str:
    return "data: [DONE]\n\n"

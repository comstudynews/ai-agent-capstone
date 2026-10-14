"""Local-first API. Demo mode runs without a paid model or external services."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.contracts import ChatIn, CreateTicketIn
from app.core import process
from app.store import create_ticket
from app.streaming import frame

load_dotenv()
logger = logging.getLogger("capstone")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = None
    app.state.checkpoint_scope = None
    if os.environ.get("AGENT_MODE", "demo") == "llm":
        from app.agent import build_agent
        from app.checkpoint import checkpointer_context
        scope = checkpointer_context()
        saver = await scope.__aenter__()
        try:
            app.state.agent = await build_agent(checkpointer=saver)
            app.state.checkpoint_scope = scope
            yield
        finally:
            await scope.__aexit__(None, None, None)
    else:
        yield


app = FastAPI(title="Fictional Operations Agent", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-Demo-Admin-Key"])


@app.get("/health")
async def health():
    return {"status": "ok", "mode": os.environ.get("AGENT_MODE", "demo")}


async def answer(message: str, thread_id: str) -> dict:
    if os.environ.get("AGENT_MODE", "demo") != "llm":
        return process(message, thread_id)
    result = await app.state.agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    last = result["messages"][-1].content
    text = last if isinstance(last, str) else str(last)
    return {"thread_id": thread_id, "answer": text, "events": []}


@app.post("/chat")
async def chat(body: ChatIn):
    thread = body.thread_id or str(uuid4())
    try:
        return await answer(body.message, thread)
    except Exception:
        logger.exception("chat error")
        raise HTTPException(503, detail={"code": "AGENT_UNAVAILABLE", "message": "요청 처리 실패"})


@app.post("/chat/stream")
async def chat_stream(body: ChatIn):
    thread = body.thread_id or str(uuid4())

    async def generate():
        yield frame("start", {"thread_id": thread})
        try:
            if os.environ.get("AGENT_MODE", "demo") == "llm":
                async for mode, data in app.state.agent.astream(
                    {"messages": [{"role": "user", "content": body.message}]},
                    config={"configurable": {"thread_id": thread}},
                    stream_mode=["messages", "updates"],
                ):
                    if mode == "messages":
                        msg, metadata = data
                        from langchain_core.messages import AIMessageChunk
                        if isinstance(msg, AIMessageChunk):
                            value = msg.content
                            if isinstance(value, str) and value:
                                yield frame("token", {"content": value})
                    else:
                        for node in data:
                            yield frame("state", {"node": node, "status": "updated"})
            else:
                result = process(body.message, thread)
                for step in result["events"]:
                    yield frame("state", {"node": step["node"], "status": step["status"]})
                    await asyncio.sleep(0)
                for i in range(0, len(result["answer"]), 16):
                    yield frame("token", {"content": result["answer"][i:i+16]})
                    await asyncio.sleep(0)
            yield frame("done", {"thread_id": thread, "finish_reason": "stop"})
        except asyncio.CancelledError:
            logger.info("stream cancelled for thread %s", thread)
            raise
        except Exception:
            logger.exception("stream failed")
            yield frame("error", {"code": "AGENT_UNAVAILABLE", "message": "작업이 실패했습니다."})

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


class UIMessage(BaseModel):
    role: str
    parts: list[dict] = Field(default_factory=list)


class UIChatIn(BaseModel):
    id: str | None = None
    messages: list[UIMessage]


@app.post("/chat/ui-stream")
async def ui_stream(body: UIChatIn):
    """Small UI Message Stream v1 adapter. External AI SDK JS build not validated here."""
    from app.ui_protocol import ui_done, ui_frame
    user_messages = [m for m in body.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(422, detail="A user message is required")
    message = " ".join(str(p.get("text", "")) for p in user_messages[-1].parts
                       if p.get("type") == "text").strip()
    if not message:
        raise HTTPException(422, detail="A nonempty text part is required")
    thread = body.id or str(uuid4())
    text_id = "txt_" + uuid4().hex
    message_id = "msg_" + uuid4().hex

    async def generate():
        yield ui_frame({"type": "start", "messageId": message_id})
        yield ui_frame({"type": "start-step"})
        yield ui_frame({"type": "text-start", "id": text_id})
        try:
            result = await answer(message, thread)
            for index in range(0, len(result["answer"]), 20):
                yield ui_frame({"type": "text-delta", "id": text_id,
                                "delta": result["answer"][index:index + 20]})
                await asyncio.sleep(0)
            yield ui_frame({"type": "text-end", "id": text_id})
            yield ui_frame({"type": "finish-step"})
            yield ui_frame({"type": "finish"})
        except Exception:
            logger.exception("UI stream failure")
            yield ui_frame({"type": "error", "errorText": "요청 처리에 실패했습니다."})
        yield ui_done()

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "x-vercel-ai-ui-message-stream": "v1",
                                      "X-Accel-Buffering": "no"})


@app.post("/tickets/approve")
async def approve_ticket(body: CreateTicketIn, x_demo_admin_key: str | None = Header(default=None)):
    """Protected *local* demo endpoint; not a production authentication flow.

    Explicit human approval occurs when user provides admin key through a trusted interface.
    """
    expected = os.environ.get("DEMO_ADMIN_KEY", "")
    if not expected or expected == "replace-with-your-private-random-secret":
        raise HTTPException(503, "Set a private DEMO_ADMIN_KEY before enabling writes")
    import secrets
    if not x_demo_admin_key or not secrets.compare_digest(x_demo_admin_key, expected):
        raise HTTPException(403, "Write operation requires approval key")
    return create_ticket(body.title, body.description, body.request_id)

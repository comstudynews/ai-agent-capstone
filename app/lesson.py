"""Recipe checkpoints: each step has an executable verification target."""
import argparse
import json
from app.core import plan, process, route, validator
from app.knowledge import get_runbook, search_manual, monitoring_status
from app.streaming import frame, SSEParser
from app.evaluation import run_evaluation
from app.store import create_ticket, search_tickets, history


def run(number: int) -> dict:
    if number == 1:
        return {"capabilities": ["Tool: manual_search", "Resource: runbook",
                                 "Tool: ticket_search", "Tool: ticket_create",
                                 "Tool: monitoring", "Prompt: diagnosis"]}
    if number == 2:
        return {"manual": search_manual("500"), "runbook": get_runbook("http-500")}
    if number == 3:
        return {"boundary": "Browser => FastAPI => Agent => MCP Client => Server"}
    if number == 4:
        return {"backend_result": process("payment-api 500 장애 상태", "lesson-04")}
    if number == 5:
        return {"history": history("lesson-04"), "thread_id": "lesson-04"}
    if number == 6:
        return {"event": frame("start", {"thread_id": "lesson-06"})}
    if number == 7:
        parser = SSEParser()
        parser.feed(frame("token", {"content": "hello"})[:15])
        return {"parsed": parser.feed(frame("token", {"content": "hello"})[15:])}
    if number == 8:
        return {"state_events": process("payment-api 500 상태", "lesson-08")["events"]}
    if number == 9:
        return {"evaluation": run_evaluation()}
    if number == 10:
        return {"missing_status": monitoring_status("absent-service")}
    if number == 11:
        return {"latency_ms": process("DB 매뉴얼", "lesson-11")["latency_ms"]}
    if number == 12:
        return {"stored_messages": len(history("lesson-04")),
                "note": "PostgreSQL persistence requires agent extra + running database"}
    if number == 13:
        return {"route": route("payment-api 500 상태"), "validation": validator([{"id": 1}], "ok")}
    if number == 14:
        return {"plan": plan("payment-api 500 장애", "DEGRADED")}
    if number == 15:
        return {"evaluation": run_evaluation(), "capstone": process("payment-api 500", "lesson-15")}
    raise ValueError("Recipe number must be 1..15")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("recipe", type=int, choices=range(1, 16))
    args = parser.parse_args()
    print(json.dumps(run(args.recipe), ensure_ascii=False, indent=2))

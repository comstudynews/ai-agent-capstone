"""Deterministic, offline-first orchestrator. Never claims to be a trained LLM."""
import re
from dataclasses import dataclass, field
from time import perf_counter
from app.knowledge import get_runbook, monitoring_status, search_manual
from app.store import search_tickets, history, remember


@dataclass
class Trace:
    route: str
    steps: list[dict] = field(default_factory=list)
    started: float = field(default_factory=perf_counter)

    def record(self, name: str, result: object) -> None:
        self.steps.append({"node": name, "status": "completed", "result": result})

    @property
    def elapsed_ms(self) -> float:
        return round((perf_counter() - self.started) * 1000, 2)


def route(question: str) -> str:
    lowered = question.lower()
    if any(x in lowered for x in ("상태", "장애", "500", "api", "서버", "모니터링")):
        return "incident"
    if any(x in lowered for x in ("티켓", "ticket", "jira")):
        return "ticket"
    return "manual"


def validator(evidence: list[dict], answer: str) -> dict:
    valid = bool(answer.strip()) and bool(evidence)
    return {"valid": valid, "evidence_count": len(evidence),
            "reason": "근거 확인" if valid else "조회 가능한 근거 없음"}


def plan(question: str, status: str | None = None) -> list[str]:
    """Explainable, bounded demo planner; does not invent model reasoning."""
    steps = ["monitoring", "runbook"] if route(question) == "incident" else ["manual"]
    if status == "DEGRADED" and "ticket_search" not in steps:
        steps.append("ticket_search")
    return steps[:3]


def process(question: str, thread_id: str) -> dict:
    """Offline reproducible capstone. Read-only; creation requires a separate approved API."""
    started = perf_counter()
    previous = history(thread_id)
    decision = route(question)
    trace = Trace(route=decision)
    evidence: list[dict] = []
    if decision == "incident":
        service = "payment-api" if "payment" in question.lower() or "결제" in question else "payment-api"
        current = monitoring_status(service)
        trace.record("monitoring", current)
        evidence.append({"source": "monitoring", **current})
        try:
            manual = get_runbook("http-500")
            trace.record("runbook", {"source": "runbook://incident/http-500"})
            evidence.append({"source": "runbook://incident/http-500", "excerpt": manual})
        except KeyError:
            pass
        if current.get("status") == "DEGRADED":
            tickets = search_tickets("API")
            trace.record("ticket_search", {"count": len(tickets)})
            evidence += [{"source": "tickets", **ticket} for ticket in tickets]
        summary = (f"{service} 상태는 {current['status']}입니다. "
                   f"권장 절차: {evidence[1]['excerpt'] if len(evidence) > 1 else 'Runbook 없음'}. "
                   "티켓 생성은 별도의 사용자 승인 절차가 필요합니다.")
    elif decision == "ticket":
        tickets = search_tickets("API")
        trace.record("ticket_search", {"count": len(tickets)})
        evidence = [{"source": "tickets", **ticket} for ticket in tickets]
        summary = "기존 티켓: " + (", ".join(t['ticket_id'] for t in tickets) if tickets else "조회 결과 없음")
    else:
        hits = search_manual("500" if "500" in question else "DB" if "db" in question.lower() else "API")
        trace.record("manual_search", {"count": len(hits)})
        evidence = hits
        summary = "관련 매뉴얼: " + ("; ".join(hit['excerpt'] for hit in hits) if hits else "조회 결과 없음")
    validation = validator(evidence, summary)
    trace.record("validator", validation)
    if not validation["valid"]:
        summary = "확인 가능한 근거가 없어 단정할 수 없습니다. 관리자에게 확인하세요."
    remember(thread_id, "user", question)
    remember(thread_id, "assistant", summary)
    return {"thread_id": thread_id, "answer": summary, "events": trace.steps,
            "route": decision, "plan": plan(question, "DEGRADED" if decision == "incident" else None),
            "evidence": evidence, "previous_messages": len(previous),
            "latency_ms": round((perf_counter() - started) * 1000, 2)}

"""규칙 기반 운영 지원 예제. 실제 LLM 실행과 구분합니다."""
import re
from dataclasses import dataclass, field
from time import perf_counter

from app.knowledge import get_runbook, monitoring_status, search_manual
from app.store import history, remember, search_tickets


SERVICE_PATTERN = re.compile(r"(?<![a-z0-9-])([a-z][a-z0-9-]*-api)(?![a-z0-9-])", re.I)
FOLLOWUP_HINTS = ("그 서비스", "해당 서비스", "그건", "그것", "아까", "앞서", "이전", "계속")


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
    has_ticket = any(term in lowered for term in ("티켓", "ticket", "jira"))
    has_incident = any(term in lowered for term in
                       ("장애", "500", "api", "서버", "모니터링", "서비스 상태", "서비스", "조치"))
    # '티켓 상태'는 장애 모니터링이 아니라 티켓 조회입니다.
    if has_ticket and not has_incident:
        return "ticket"
    if has_incident or ("상태" in lowered and not has_ticket):
        return "incident"
    if has_ticket:
        return "ticket"
    return "manual"


def extract_service(question: str) -> str | None:
    """질문에 명시된 서비스만 선택합니다. 이름을 임의로 만들어 내지 않습니다."""
    match = SERVICE_PATTERN.search(question)
    if match:
        return match.group(1).lower()
    if "결제" in question:
        return "payment-api"
    return None


def validator(evidence: list[dict], answer: str) -> dict:
    valid = bool(answer.strip()) and bool(evidence)
    return {"valid": valid, "evidence_count": len(evidence),
            "reason": "근거 확인" if valid else "조회 가능한 근거 없음"}


def plan(question: str, status: str | None = None) -> list[str]:
    """최대 3단계까지 실행하는 교육용 규칙 기반 계획입니다."""
    steps = ["monitoring", "runbook"] if route(question) == "incident" else ["manual"]
    if status == "DEGRADED" and "ticket_search" not in steps:
        steps.append("ticket_search")
    return steps[:3]


def process(question: str, thread_id: str) -> dict:
    """이전 대화의 서비스명을 활용하되, 관찰되지 않은 값을 만들어 내지 않습니다."""
    started = perf_counter()
    previous = history(thread_id)
    explicit_service = extract_service(question)
    last_user = next((m["content"] for m in reversed(previous) if m["role"] == "user"), "")
    followup = any(hint in question for hint in FOLLOWUP_HINTS)
    inherited_service = extract_service(last_user) if not explicit_service else None
    service = explicit_service or inherited_service
    decision = route(question)
    if followup and decision == "manual" and last_user:
        decision = route(last_user)

    trace = Trace(route=decision)
    evidence: list[dict] = []
    current_status = None

    if decision == "incident":
        if not service:
            summary = "확인할 서비스명을 알려주세요. 예: payment-api 상태"
        else:
            current = monitoring_status(service)
            trace.record("monitoring", current)
            current_status = current["status"]
            if current_status == "NOT_FOUND":
                summary = f"{service}의 모니터링 데이터를 찾을 수 없습니다. 서비스명을 확인해 주세요."
            else:
                evidence.append({"source": "monitoring", **current})
                if current_status != "OK":
                    try:
                        manual = get_runbook("http-500")
                        trace.record("runbook", {"source": "runbook://incident/http-500"})
                        evidence.append({"source": "runbook://incident/http-500", "excerpt": manual})
                    except KeyError:
                        pass
                if current_status == "DEGRADED":
                    tickets = search_tickets("API")
                    trace.record("ticket_search", {"count": len(tickets)})
                    evidence.extend({"source": "tickets", **ticket} for ticket in tickets)
                procedure = next((hit["excerpt"] for hit in evidence if hit["source"].startswith("runbook://")), None)
                summary = f"{service} 상태는 {current_status}입니다."
                if procedure:
                    summary += f" 권장 절차: {procedure}."
                summary += " 티켓 생성에는 별도의 사용자 승인이 필요합니다."
                if inherited_service and not explicit_service:
                    summary = "이전 질문의 서비스를 기준으로 확인했습니다. " + summary
    elif decision == "ticket":
        # 특정 서비스가 없으면 목 데이터의 전체 티켓을 조회합니다.
        tickets = search_tickets(service or "")
        trace.record("ticket_search", {"count": len(tickets)})
        evidence = [{"source": "tickets", **ticket} for ticket in tickets]
        summary = "기존 티켓: " + (", ".join(t["ticket_id"] for t in tickets) if tickets else "조회 결과 없음")
    else:
        hits = search_manual("500" if "500" in question else "DB" if "db" in question.lower() else "API")
        trace.record("manual_search", {"count": len(hits)})
        evidence = hits
        summary = "관련 매뉴얼: " + ("; ".join(hit["excerpt"] for hit in hits) if hits else "조회 결과 없음")

    validation = validator(evidence, summary)
    trace.record("validator", validation)
    # 데이터가 없는 경우에는 근거 부족을 알리되, 어떤 서비스를 조회했는지 숨기지 않습니다.
    if not validation["valid"] and decision == "manual":
        summary = "관련 매뉴얼을 찾지 못했습니다. 검색어를 바꿔 주세요."
    remember(thread_id, "user", question)
    remember(thread_id, "assistant", summary)

    return {"thread_id": thread_id, "answer": summary, "events": trace.steps,
            "route": decision, "plan": plan(question, current_status),
            "evidence": evidence, "previous_messages": len(previous),
            "latency_ms": round((perf_counter() - started) * 1000, 2)}

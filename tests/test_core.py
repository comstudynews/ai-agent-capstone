from app.core import process, plan, route
from app.evaluation import run_evaluation

def test_offline_agent_tools_and_evidence():
    x = process("payment-api 500 상태", "abc-thread")
    assert x["route"] == "incident"
    assert any(e["node"] == "monitoring" for e in x["events"])
    assert x["evidence"] and x["answer"]
    assert process("payment-api 500 상태", "abc-thread")["previous_messages"] == 2

def test_routing_and_dynamic_plan():
    assert route("티켓 목록") == "ticket"
    assert plan("payment-api 상태", "DEGRADED") == ["monitoring", "runbook", "ticket_search"]

def test_evaluation():
    score = run_evaluation()
    assert score["passed"] == score["total"] == 3

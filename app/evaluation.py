"""Deterministic evaluations: verify tool effects, not exact LLM phrasing."""
from app.core import process
from app.knowledge import search_manual

DATASET = [
    {"question": "payment-api 500 장애 상태", "expected_route": "incident"},
    {"question": "티켓을 조회해줘", "expected_route": "ticket"},
    {"question": "DB 매뉴얼은?", "expected_route": "manual"},
]


def run_evaluation() -> dict:
    results = []
    for idx, sample in enumerate(DATASET):
        result = process(sample["question"], f"eval-{idx}")
        results.append({"question": sample["question"],
                        "passed": result["route"] == sample["expected_route"],
                        "route": result["route"], "latency_ms": result["latency_ms"]})
    return {"passed": sum(r["passed"] for r in results), "total": len(results),
            "details": results}


if __name__ == "__main__":
    import json
    print(json.dumps(run_evaluation(), ensure_ascii=False, indent=2))

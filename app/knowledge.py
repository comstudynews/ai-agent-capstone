"""Fictional sources, reused by MCP tools and the offline demonstration."""
from app.contracts import SearchHit

MANUALS = {
    "MAN-500": ("API 500 장애 대응", "HTTP 500 오류: 서비스 로그와 의존 DB 연결을 확인한다."),
    "MAN-DB": ("DB 연결 점검", "DB 연결 장애: 접속 계정, 네트워크, 연결 풀과 포트를 확인한다."),
    "MAN-LATENCY": ("응답 지연 조치", "API 응답 지연: P95 지연과 최근 배포 내역을 점검한다."),
}
RUNBOOKS = {
    "http-500": "서버 로그 확인 → DB 연결 확인 → 최근 변경 검토 → 롤백 여부 판단",
    "db-down": "DB 포트 확인 → 계정 권한 확인 → 연결 풀 재설정 여부 판단",
}
MONITORING = {"payment-api": {"service": "payment-api", "status": "DEGRADED", "http_5xx": 12}}


def search_manual(keyword: str) -> list[dict]:
    """Simple searchable fallback, not vector search; returns a consistent contract."""
    term = keyword.strip().lower()
    if not term:
        raise ValueError("검색어가 비어 있습니다")
    hits = []
    for doc_id, (title, text) in MANUALS.items():
        if term in (title + " " + text + " " + doc_id).lower():
            hits.append(SearchHit(id=doc_id, title=title, excerpt=text,
                                  score=1.0, source=f"manual://{doc_id}").model_dump())
    return hits


def get_runbook(incident_type: str) -> str:
    if incident_type not in RUNBOOKS:
        raise KeyError("RUNBOOK_NOT_FOUND")
    return RUNBOOKS[incident_type]


def monitoring_status(service: str) -> dict:
    if service not in MONITORING:
        return {"service": service, "status": "NOT_FOUND"}
    return MONITORING[service]

"""Actual stdio MCP server. Requires `uv sync --extra agent`.

Do not print to stdout while stdio protocol is active.
"""
from mcp.server.fastmcp import FastMCP
from app.knowledge import get_runbook, monitoring_status
from app.rag import retrieve
from app.store import search_tickets
from app.approval import create_approved_ticket

mcp = FastMCP("Fictional Operations Assistant")


@mcp.tool()
def search_operations_manual(keyword: str) -> list[dict]:
    """Search operational manuals by keyword, returning source IDs and excerpts."""
    return retrieve(keyword)


@mcp.tool()
def search_issue_tickets(keyword: str) -> list[dict]:
    """Search demo issue tickets. This is a read-only tool."""
    return search_tickets(keyword)


@mcp.tool()
def read_monitoring_status(service: str) -> dict:
    """Read fictional monitoring status for a service."""
    return monitoring_status(service)


@mcp.tool()
def create_issue_ticket(title: str, description: str, request_id: str,
                        approval_token: str) -> dict:
    """요청 내용과 만료시간에 서명된 승인 토큰 없이는 실행할 수 없습니다."""
    return create_approved_ticket(title, description, request_id, approval_token)


@mcp.resource("runbook://incident/{incident_type}")
def read_runbook(incident_type: str) -> str:
    """Read a static runbook by incident type."""
    return get_runbook(incident_type)


@mcp.prompt()
def incident_diagnosis(service: str) -> str:
    """Reusable diagnostic sequence for an operational incident."""
    return (f"Investigate {service}: check monitoring, retrieve runbook, search existing tickets, "
            "report evidence, and request approval before mutating anything.")


if __name__ == "__main__":
    mcp.run(transport="stdio")

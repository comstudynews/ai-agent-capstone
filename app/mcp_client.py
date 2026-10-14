"""MCP stdio 검증: Tool·Resource·Prompt와 승인된 생성 작업을 테스트합니다.

실행: uv run --extra agent python -m app.mcp_client
"""
import asyncio
import os
import sys
from uuid import uuid4

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl

from app.approval import issue_approval_token

load_dotenv()


async def inspect() -> dict:
    parameters = StdioServerParameters(command=sys.executable, args=["-m", "app.mcp_server"])
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            if len(names) != 4 or "create_issue_ticket" not in names:
                raise RuntimeError("MCP Tool 목록이 예상과 다릅니다.")
            resource = await session.read_resource(AnyUrl("runbook://incident/http-500"))
            prompt = await session.get_prompt("incident_diagnosis", {"service": "payment-api"})
            called = await session.call_tool("read_monitoring_status", {"service": "payment-api"})
            if called.isError:
                raise RuntimeError("MCP 모니터링 Tool 호출이 실패했습니다.")

            sample = {
                "title": "Test API ticket",
                "description": "Repeated HTTP 500 errors in fictional environment",
                "request_id": f"mcp-test-{uuid4().hex}",
            }
            try:
                denied_result = await session.call_tool("create_issue_ticket", sample)
                denied = bool(denied_result.isError)
            except Exception:
                denied = True
            if not denied:
                raise RuntimeError("MCP 티켓 생성 Tool이 승인 없이 실행됐습니다.")

            approved = False
            if os.getenv("DEMO_ADMIN_KEY") or os.getenv("MCP_APPROVAL_SIGNING_KEY"):
                token = issue_approval_token(**sample)
                result = await session.call_tool(
                    "create_issue_ticket", {**sample, "approval_token": token})
                if result.isError:
                    raise RuntimeError("승인된 MCP 티켓 생성이 실패했습니다: " + str(result.content)[:600])
                retry = await session.call_tool(
                    "create_issue_ticket", {**sample, "approval_token": token})
                if retry.isError:
                    raise RuntimeError("동일 요청 ID 재실행이 실패했습니다.")
                approved = True

            return {
                "tools": names,
                "resource": str(resource.contents),
                "prompt": str(prompt.messages),
                "tool_result": str(called.content),
                "unapproved_write_rejected": denied,
                "approved_write_checked": approved,
            }


if __name__ == "__main__":
    print(asyncio.run(inspect()))

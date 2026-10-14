"""Direct MCP protocol validation: tools + Resource + Prompt.

Run: uv run --extra agent python -m app.mcp_client.
"""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from pydantic import AnyUrl
from mcp.client.stdio import stdio_client


async def inspect() -> dict:
    parameters = StdioServerParameters(command=sys.executable, args=["-m", "app.mcp_server"])
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            resource = await session.read_resource(AnyUrl("runbook://incident/http-500"))
            prompt = await session.get_prompt("incident_diagnosis", {"service": "payment-api"})
            called = await session.call_tool("read_monitoring_status", {"service": "payment-api"})
            return {"tools": [x.name for x in tools.tools],
                    "resource": str(resource.contents), "prompt": str(prompt.messages),
                    "tool_result": str(called.content)}


if __name__ == "__main__":
    print(asyncio.run(inspect()))

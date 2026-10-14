"""LangChain 1.x / MCP adapter integration. Read-only agent by design."""
import os
import sys
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient


async def build_agent(checkpointer=None):
    client = MultiServerMCPClient({
        "operations": {"transport": "stdio", "command": sys.executable,
                       "args": ["-m", "app.mcp_server"]}
    })
    tools = await client.get_tools()
    # A model cannot trigger a write operation; approval is handled by a protected API endpoint.
    readonly = [tool for tool in tools if tool.name != "create_issue_ticket"]
    model_name = os.environ.get("OPENAI_MODEL", "")
    if not model_name or not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_MODEL and OPENAI_API_KEY must be set in AGENT_MODE=llm")
    agent = create_agent(model=ChatOpenAI(model=model_name), tools=readonly,
                         system_prompt=("You are an IT operations assistant. "
                                        "Only cite evidence returned from tools. "
                                        "Do not create tickets or claim to have run unobserved tools."),
                         checkpointer=checkpointer)
    return agent

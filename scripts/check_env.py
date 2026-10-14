import importlib.metadata as metadata
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
print("Python project root:", Path.cwd())
for name in ("fastapi", "pydantic", "uvicorn", "httpx"):
    print(name, metadata.version(name))
print("Agent mode:", os.environ.get("AGENT_MODE", "demo"))
print("API key:", "configured" if os.environ.get("OPENAI_API_KEY") else "absent (fine for demo)")

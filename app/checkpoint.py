"""Checkpointer selection; Postgres setup must complete before serving traffic."""
import os
from contextlib import asynccontextmanager


@asynccontextmanager
async def checkpointer_context():
    if os.environ.get("CHECKPOINT_MODE", "memory") == "postgres":
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        async with AsyncPostgresSaver.from_conn_string(os.environ["DATABASE_URL"]) as saver:
            await saver.setup()  # migrate separately in production
            yield saver
    else:
        from langgraph.checkpoint.memory import InMemorySaver
        yield InMemorySaver()

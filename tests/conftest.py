import os
import pytest

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "demo.sqlite3"))
    monkeypatch.setenv("AGENT_MODE", "demo")

"""Transactional SQLite demo store. Never store real business or personal data."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DEFAULT_DB = "./data/capstone.sqlite3"


class IdempotencyConflictError(ValueError):
    """동일한 request_id로 서로 다른 티켓 데이터를 제출했습니다."""


def db_path() -> Path:
    return Path(os.environ.get("DATABASE_PATH", DEFAULT_DB)).resolve()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=15)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA busy_timeout = 15000")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("""CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            request_id TEXT NOT NULL UNIQUE
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )""")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_ticket(title: str, description: str, request_id: str) -> dict:
    """Idempotent across processes; unique key prevents a second row."""
    if len(title.strip()) < 5 or len(description.strip()) < 10 or len(request_id) < 8:
        raise ValueError("Invalid ticket data")
    with connect() as db:
        inserted = True
        try:
            db.execute("INSERT INTO tickets(title, description, request_id) VALUES (?,?,?)",
                       (title, description, request_id))
        except sqlite3.IntegrityError:
            inserted = False
        row = db.execute("SELECT * FROM tickets WHERE request_id=?", (request_id,)).fetchone()
        if row is None:
            raise RuntimeError("티켓 저장 결과를 확인할 수 없습니다.")
        if row["title"] != title or row["description"] != description:
            raise IdempotencyConflictError("같은 요청 ID로 다른 티켓 내용을 등록할 수 없습니다.")
        return {"ticket_id": f"DEMO-{row['id']}", "title": row['title'],
                "description": row['description'], "status": row['status'],
                "created": inserted}


def search_tickets(keyword: str) -> list[dict]:
    with connect() as db:
        rows = db.execute("SELECT * FROM tickets WHERE lower(title) LIKE ? ORDER BY id",
                          (f"%{keyword.lower()}%",)).fetchall()
        return [{"ticket_id": f"DEMO-{r['id']}", "title": r['title'],
                 "description": r['description'], "status": r['status']} for r in rows]


def remember(thread_id: str, role: str, content: str) -> None:
    with connect() as db:
        db.execute("INSERT INTO messages(thread_id,role,content) VALUES (?,?,?)",
                   (thread_id, role, content))


def history(thread_id: str, limit: int = 12) -> list[dict]:
    with connect() as db:
        rows = db.execute("SELECT role,content FROM messages WHERE thread_id=? ORDER BY id DESC LIMIT ?",
                          (thread_id, limit)).fetchall()
        return [dict(r) for r in reversed(rows)]

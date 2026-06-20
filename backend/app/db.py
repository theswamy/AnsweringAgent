"""SQLite persistence for call logs, full conversation transcripts, and the
user-editable agent settings. Everything the agent says or hears is stored here.

A thin module-level helper layer keeps the rest of the app free of SQL.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from .config import get_settings

_local = threading.local()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _conn() -> sqlite3.Connection:
    """One connection per thread (SQLite connections are not thread-safe)."""
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(get_settings().database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        _local.conn = conn
    return conn


def init_db() -> None:
    c = _conn()
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id              INTEGER PRIMARY KEY CHECK (id = 1),
            user_name       TEXT NOT NULL DEFAULT 'the owner',
            user_phone      TEXT NOT NULL DEFAULT '',
            agent_defaults  TEXT NOT NULL DEFAULT '',
            send_transcript_sms INTEGER NOT NULL DEFAULT 1,
            updated_at      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS calls (
            call_sid           TEXT PRIMARY KEY,
            from_number        TEXT,
            to_number          TEXT,
            started_at         TEXT NOT NULL,
            ended_at           TEXT,
            status             TEXT NOT NULL DEFAULT 'in-progress',
            caller_name        TEXT,
            intent             TEXT,
            callback_requested INTEGER NOT NULL DEFAULT 0,
            callback_number    TEXT,
            callback_time      TEXT,
            is_automated       INTEGER NOT NULL DEFAULT 0,
            summary            TEXT
        );

        CREATE TABLE IF NOT EXISTS turns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid    TEXT NOT NULL,
            role        TEXT NOT NULL,         -- 'caller' | 'agent'
            text        TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            FOREIGN KEY (call_sid) REFERENCES calls (call_sid)
        );
        """
    )
    # Seed the singleton settings row if absent.
    if c.execute("SELECT 1 FROM settings WHERE id = 1").fetchone() is None:
        c.execute(
            "INSERT INTO settings (id, agent_defaults, updated_at) VALUES (1, ?, ?)",
            (DEFAULT_AGENT_DEFAULTS, _now()),
        )
    c.commit()


DEFAULT_AGENT_DEFAULTS = (
    "If the caller is an automated system, an IVR menu, or another AI agent: do "
    "not share personal details, do not press menu options, and do not confirm or "
    "schedule anything. Politely ask them to send the details by text or email so "
    "the owner can review, then end the call."
)


# --- Settings ---------------------------------------------------------------

def get_user_settings() -> dict[str, Any]:
    row = _conn().execute("SELECT * FROM settings WHERE id = 1").fetchone()
    return dict(row)


def update_user_settings(**fields: Any) -> dict[str, Any]:
    allowed = {"user_name", "user_phone", "agent_defaults", "send_transcript_sms"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if updates:
        cols = ", ".join(f"{k} = ?" for k in updates)
        params = list(updates.values()) + [_now()]
        _conn().execute(f"UPDATE settings SET {cols}, updated_at = ? WHERE id = 1", params)
        _conn().commit()
    return get_user_settings()


# --- Calls ------------------------------------------------------------------

def create_call(call_sid: str, from_number: str, to_number: str) -> None:
    _conn().execute(
        "INSERT OR IGNORE INTO calls (call_sid, from_number, to_number, started_at) "
        "VALUES (?, ?, ?, ?)",
        (call_sid, from_number, to_number, _now()),
    )
    _conn().commit()


def update_call(call_sid: str, **fields: Any) -> None:
    allowed = {
        "ended_at", "status", "caller_name", "intent", "callback_requested",
        "callback_number", "callback_time", "is_automated", "summary",
    }
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return
    cols = ", ".join(f"{k} = ?" for k in updates)
    _conn().execute(
        f"UPDATE calls SET {cols} WHERE call_sid = ?",
        list(updates.values()) + [call_sid],
    )
    _conn().commit()


def get_call(call_sid: str) -> Optional[dict[str, Any]]:
    row = _conn().execute("SELECT * FROM calls WHERE call_sid = ?", (call_sid,)).fetchone()
    return dict(row) if row else None


def list_calls(limit: int = 100) -> list[dict[str, Any]]:
    rows = _conn().execute(
        "SELECT * FROM calls ORDER BY started_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


# --- Turns (transcript) -----------------------------------------------------

def add_turn(call_sid: str, role: str, text: str) -> None:
    _conn().execute(
        "INSERT INTO turns (call_sid, role, text, created_at) VALUES (?, ?, ?, ?)",
        (call_sid, role, text, _now()),
    )
    _conn().commit()


def get_turns(call_sid: str) -> list[dict[str, Any]]:
    rows = _conn().execute(
        "SELECT role, text, created_at FROM turns WHERE call_sid = ? ORDER BY id",
        (call_sid,),
    ).fetchall()
    return [dict(r) for r in rows]


def transcript_text(call_sid: str) -> str:
    """Human-readable transcript for SMS / display."""
    s = get_user_settings()
    name = s["user_name"]
    lines = []
    for t in get_turns(call_sid):
        speaker = f"{name}'s agent" if t["role"] == "agent" else "Caller"
        lines.append(f"{speaker}: {t['text']}")
    return "\n".join(lines)

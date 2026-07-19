"""SQLite persistence: which topics/shows to follow, how far the back-catalog
walk has progressed, which episodes were already summarized, and an archive of
sent newsletters.

Everything is small and single-user, so a file-backed SQLite DB is plenty. All
access goes through short-lived connections to stay safe across the scheduler
thread and the web request handlers.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from typing import Iterator

from .config import get_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    genre_id INTEGER NOT NULL,
    enabled  INTEGER NOT NULL DEFAULT 1,
    UNIQUE(genre_id)
);

-- Shows the user explicitly follows. These are the ones the "one prior episode a
-- day" back-catalog walk steps through. `cursor` is the index into the feed
-- (0 = newest) of the next-oldest episode to summarize.
CREATE TABLE IF NOT EXISTS shows (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    itunes_id   TEXT,
    title       TEXT NOT NULL,
    feed_url    TEXT NOT NULL,
    apple_url   TEXT,
    artwork_url TEXT,
    cursor      INTEGER NOT NULL DEFAULT 0,
    added_at    TEXT NOT NULL,
    UNIQUE(feed_url)
);

-- Dedupe: every episode we've ever summarized in a newsletter.
CREATE TABLE IF NOT EXISTS sent_episodes (
    show_id      INTEGER NOT NULL,
    episode_guid TEXT NOT NULL,
    sent_on      TEXT NOT NULL,
    PRIMARY KEY (show_id, episode_guid)
);

CREATE TABLE IF NOT EXISTS newsletters (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    for_date TEXT NOT NULL,
    subject  TEXT NOT NULL,
    html     TEXT NOT NULL,
    sent     INTEGER NOT NULL DEFAULT 0,
    created  TEXT NOT NULL
);
"""

# Sensible starting topics for a tech/venture reader. Editable from the web UI.
_DEFAULT_TOPICS = [("Technology", 1318), ("Business", 1321), ("News", 1489)]


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(get_settings().database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _conn() as conn:
        conn.executescript(_SCHEMA)
        existing = conn.execute("SELECT COUNT(*) AS n FROM topics").fetchone()["n"]
        if existing == 0:
            conn.executemany(
                "INSERT OR IGNORE INTO topics (name, genre_id) VALUES (?, ?)",
                _DEFAULT_TOPICS,
            )


# --------------------------------------------------------------------------- #
# Topics                                                                       #
# --------------------------------------------------------------------------- #

def list_topics(enabled_only: bool = False) -> list[dict]:
    sql = "SELECT * FROM topics"
    if enabled_only:
        sql += " WHERE enabled = 1"
    sql += " ORDER BY name"
    with _conn() as conn:
        return [dict(r) for r in conn.execute(sql).fetchall()]


def add_topic(name: str, genre_id: int) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO topics (name, genre_id, enabled) VALUES (?, ?, 1)",
            (name, genre_id),
        )


def set_topic_enabled(topic_id: int, enabled: bool) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE topics SET enabled = ? WHERE id = ?", (1 if enabled else 0, topic_id)
        )


def remove_topic(topic_id: int) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))


# --------------------------------------------------------------------------- #
# Followed shows                                                               #
# --------------------------------------------------------------------------- #

def list_shows() -> list[dict]:
    with _conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM shows ORDER BY title").fetchall()]


def add_show(
    title: str,
    feed_url: str,
    itunes_id: str | None = None,
    apple_url: str | None = None,
    artwork_url: str | None = None,
) -> int:
    with _conn() as conn:
        cur = conn.execute(
            """INSERT OR IGNORE INTO shows
               (itunes_id, title, feed_url, apple_url, artwork_url, added_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (itunes_id, title, feed_url, apple_url, artwork_url, date.today().isoformat()),
        )
        if cur.lastrowid:
            return cur.lastrowid
        row = conn.execute("SELECT id FROM shows WHERE feed_url = ?", (feed_url,)).fetchone()
        return int(row["id"])


def remove_show(show_id: int) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM shows WHERE id = ?", (show_id,))
        conn.execute("DELETE FROM sent_episodes WHERE show_id = ?", (show_id,))


def advance_cursor(show_id: int) -> None:
    """Move a show's back-catalog pointer one episode older."""
    with _conn() as conn:
        conn.execute("UPDATE shows SET cursor = cursor + 1 WHERE id = ?", (show_id,))


def set_cursor(show_id: int, value: int) -> None:
    """Point a show's back-catalog pointer at a specific feed index."""
    with _conn() as conn:
        conn.execute("UPDATE shows SET cursor = ? WHERE id = ?", (value, show_id))


# --------------------------------------------------------------------------- #
# Sent-episode dedupe                                                          #
# --------------------------------------------------------------------------- #

def already_sent(show_id: int, guid: str) -> bool:
    with _conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM sent_episodes WHERE show_id = ? AND episode_guid = ?",
            (show_id, guid),
        ).fetchone()
        return row is not None


def mark_sent(show_id: int, guid: str) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sent_episodes (show_id, episode_guid, sent_on) VALUES (?, ?, ?)",
            (show_id, guid, date.today().isoformat()),
        )


# --------------------------------------------------------------------------- #
# Newsletter archive                                                           #
# --------------------------------------------------------------------------- #

def save_newsletter(for_date: str, subject: str, html: str, sent: bool) -> int:
    from datetime import datetime, timezone

    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO newsletters (for_date, subject, html, sent, created) VALUES (?, ?, ?, ?, ?)",
            (for_date, subject, html, 1 if sent else 0, datetime.now(timezone.utc).isoformat()),
        )
        return int(cur.lastrowid)


def list_newsletters(limit: int = 30) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, for_date, subject, sent, created FROM newsletters ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_newsletter(newsletter_id: int) -> dict | None:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM newsletters WHERE id = ?", (newsletter_id,)).fetchone()
        return dict(row) if row else None

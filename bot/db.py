"""SQLite persistence layer — stdlib sqlite3 only."""
import os
import sqlite3
from datetime import datetime, timezone

from . import config as _config
from .config import DATABASE_PATH, DAILY_LIMIT, HISTORY_LIMIT

_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(os.path.abspath(DATABASE_PATH)), exist_ok=True)
        _conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def init_db() -> None:
    """Create tables if they don't exist."""
    conn = _get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            username    TEXT,
            created_at  TEXT,
            usage_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS history (
            id         INTEGER PRIMARY KEY,
            user_id    INTEGER,
            type       TEXT,
            prompt     TEXT,
            result     TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS templates (
            id         INTEGER PRIMARY KEY,
            user_id    INTEGER,
            name       TEXT,
            type       TEXT,
            content    TEXT
        );
        CREATE TABLE IF NOT EXISTS settings (
            user_id   INTEGER PRIMARY KEY,
            model_key TEXT
        );
        """
    )
    conn.commit()
    # Idempotent migration: add language column if it doesn't exist yet.
    # Works for both a fresh DB and an existing production DB on a Fly volume.
    cols = {row[1] for row in conn.execute("PRAGMA table_info(settings)")}
    if "language" not in cols:
        conn.execute("ALTER TABLE settings ADD COLUMN language TEXT")
        conn.commit()


def get_or_create_user(telegram_id: int, username: str | None) -> int:
    """Return internal users.id; insert if new."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO users (telegram_id, username, created_at, usage_count) VALUES (?, ?, ?, 0)",
        (telegram_id, username, _now()),
    )
    conn.commit()
    return cur.lastrowid


def count_today(user_id: int) -> int:
    """Number of history rows for this user created today (UTC)."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM history WHERE user_id = ? AND substr(created_at, 1, 10) = ?",
        (user_id, _today()),
    ).fetchone()
    return row["cnt"]


def remaining_quota(telegram_id: int, user_id: int) -> int | None:
    """None means unlimited (admin). Otherwise remaining generations today."""
    admin_id = int(os.environ.get("ADMIN_TELEGRAM_ID", _config.ADMIN_TELEGRAM_ID))
    if telegram_id == admin_id:
        return None
    return max(0, DAILY_LIMIT - count_today(user_id))


def record_generation(user_id: int, kind: str, prompt: str, result: str) -> None:
    """Insert a history row and increment usage_count."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO history (user_id, type, prompt, result, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, kind, prompt, result, _now()),
    )
    conn.execute(
        "UPDATE users SET usage_count = usage_count + 1 WHERE id = ?",
        (user_id,),
    )
    conn.commit()


def get_history(user_id: int, limit: int = HISTORY_LIMIT) -> list[sqlite3.Row]:
    """Most recent generations first."""
    conn = _get_conn()
    return conn.execute(
        "SELECT * FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def save_template(user_id: int, name: str, kind: str, content: str) -> None:
    """Insert a template row."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO templates (user_id, name, type, content) VALUES (?, ?, ?, ?)",
        (user_id, name, kind, content),
    )
    conn.commit()


def list_templates(user_id: int) -> list[sqlite3.Row]:
    """All templates for a user, newest first."""
    conn = _get_conn()
    return conn.execute(
        "SELECT * FROM templates WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()


def get_template(user_id: int, name: str) -> sqlite3.Row | None:
    """Fetch a single template by user_id + name."""
    conn = _get_conn()
    return conn.execute(
        "SELECT * FROM templates WHERE user_id = ? AND name = ?",
        (user_id, name),
    ).fetchone()


def get_model_key(user_id: int, default: str) -> str:
    """Return the user's chosen model key, or default if unset."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT model_key FROM settings WHERE user_id = ?", (user_id,)
    ).fetchone()
    return row["model_key"] if row else default


def set_model_key(user_id: int, model_key: str) -> None:
    """Persist the user's model choice (upsert)."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO settings (user_id, model_key) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET model_key = excluded.model_key",
        (user_id, model_key),
    )
    conn.commit()


def get_lang(user_id: int) -> str | None:
    """Return the user's chosen language code, or None if not yet set."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT language FROM settings WHERE user_id = ?", (user_id,)
    ).fetchone()
    return row["language"] if row else None


def set_lang(user_id: int, lang: str) -> None:
    """Persist the user's language choice (upsert)."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO settings (user_id, language) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET language = excluded.language",
        (user_id, lang),
    )
    conn.commit()


def stats() -> dict:
    """Return total user count and total generation count."""
    conn = _get_conn()
    users = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()["cnt"]
    generations = conn.execute("SELECT COUNT(*) AS cnt FROM history").fetchone()["cnt"]
    return {"users": users, "generations": generations}


def top_users(limit: int = 5) -> list[sqlite3.Row]:
    """Users ordered by usage_count descending."""
    conn = _get_conn()
    return conn.execute(
        "SELECT username, usage_count FROM users ORDER BY usage_count DESC LIMIT ?",
        (limit,),
    ).fetchall()

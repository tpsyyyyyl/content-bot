"""Shared fixtures: temp DB + fake Update/Context factories for handler tests."""
import os
import tempfile
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

# Env must be set before importing bot modules (config reads at import time).
_tmpdir = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_PATH", os.path.join(_tmpdir, "test.db"))
os.environ.setdefault("ADMIN_TELEGRAM_ID", "999")
os.environ.setdefault("GROQ_API_KEY", "test")

import bot.config as config  # noqa: E402
import bot.db as db  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    """Give every test an empty database."""
    db._conn = None
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)
    db.init_db()
    yield
    db._conn = None
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)


def _make_message():
    return SimpleNamespace(
        text=None,
        chat_id=1,
        reply_text=AsyncMock(),
        reply_photo=AsyncMock(),
        reply_chat_action=AsyncMock(),
    )


def _make_update(text=None, user_id=1, username="tester", first_name="Tester", callback_data=None):
    message = _make_message()
    message.text = text
    user = SimpleNamespace(id=user_id, username=username, first_name=first_name)
    query = None
    if callback_data is not None:
        query = SimpleNamespace(
            data=callback_data,
            answer=AsyncMock(),
            edit_message_text=AsyncMock(),
            message=_make_message(),
            from_user=user,
        )
    return SimpleNamespace(
        effective_user=user,
        message=message,
        effective_message=query.message if query else message,
        callback_query=query,
    )


def _make_context(args=None, user_data=None):
    return SimpleNamespace(args=args or [], user_data=user_data if user_data is not None else {})


@pytest.fixture
def make_update():
    return _make_update


@pytest.fixture
def make_context():
    return _make_context

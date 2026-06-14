"""Tests for the long-message splitter helper."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

from bot.handlers._reply import _split, reply_chunks


def test_split_keeps_chunks_within_limit():
    text = "\n".join("x" * 100 for _ in range(60))  # ~6000 chars
    chunks = _split(text, limit=4096)
    assert len(chunks) >= 2
    assert all(len(c) <= 4096 for c in chunks)


def test_split_hard_splits_oversized_line():
    chunks = _split("y" * 5000, limit=4096)
    assert len(chunks) == 2
    assert all(len(c) <= 4096 for c in chunks)


async def test_reply_chunks_markup_on_last_only():
    msg = SimpleNamespace(reply_text=AsyncMock())
    text = "\n".join("x" * 100 for _ in range(60))
    await reply_chunks(msg, text, reply_markup="MK")
    calls = msg.reply_text.await_args_list
    assert len(calls) >= 2
    assert calls[0].kwargs["reply_markup"] is None
    assert calls[-1].kwargs["reply_markup"] == "MK"

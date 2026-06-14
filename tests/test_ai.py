"""Tests for bot/ai.py — monkeypatches the Groq client."""
import os

os.environ["GROQ_API_KEY"] = "test"

import pytest
from bot import ai


# ---------------------------------------------------------------------------
# Fake Groq client
# ---------------------------------------------------------------------------

class FakeMsg:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeMsg(content)


class FakeResp:
    def __init__(self, content: str):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, content: str = "hello", raises: Exception | None = None):
        self._content = content
        self._raises = raises

    def create(self, **kwargs):
        if self._raises:
            raise self._raises
        return FakeResp(self._content)


class FakeChat:
    def __init__(self, content: str = "hello", raises: Exception | None = None):
        self.completions = FakeCompletions(content=content, raises=raises)


class FakeClient:
    def __init__(self, content: str = "hello", raises: Exception | None = None):
        self.chat = FakeChat(content=content, raises=raises)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_client():
    """Ensure module-level singleton is cleared between tests."""
    original = ai._client
    ai._client = None
    yield
    ai._client = original


def make_client(content="hello", raises=None):
    return FakeClient(content=content, raises=raises)


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_generate_returns_ai_response(monkeypatch):
    monkeypatch.setattr(ai, "_get_client", lambda: make_client("hello"))
    assert ai.generate("social_post", "x") == "hello"


def test_translate_returns_ai_response(monkeypatch):
    monkeypatch.setattr(ai, "_get_client", lambda: make_client("hello"))
    assert ai.translate("en", "x") == "hello"


def test_summarize_returns_ai_response(monkeypatch):
    monkeypatch.setattr(ai, "_get_client", lambda: make_client("hello"))
    assert ai.summarize("x") == "hello"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_generate_raises_runtime_error_on_rate_limit(monkeypatch):
    monkeypatch.setattr(
        ai, "_get_client", lambda: make_client(raises=Exception("rate_limit reached"))
    )
    with pytest.raises(RuntimeError) as exc_info:
        ai.generate("social_post", "x")
    assert "rate" in exc_info.value.args[0].lower() or "⏳" in exc_info.value.args[0]

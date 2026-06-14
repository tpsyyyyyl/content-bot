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
    monkeypatch.setattr(ai.time, "sleep", lambda _s: None)  # don't wait through retries
    monkeypatch.setattr(
        ai, "_get_client", lambda: make_client(raises=Exception("rate_limit reached"))
    )
    with pytest.raises(RuntimeError) as exc_info:
        ai.generate("social_post", "x")
    assert "rate" in exc_info.value.args[0].lower() or "⏳" in exc_info.value.args[0]


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------

class FlakyCompletions:
    """Raise a rate-limit error a fixed number of times, then succeed."""

    def __init__(self, fail_times: int):
        self.fail_times = fail_times
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise Exception("429 rate_limit")
        return FakeResp("recovered")


def test_chat_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr(ai.time, "sleep", lambda _s: None)
    completions = FlakyCompletions(fail_times=2)
    client = FakeClient()
    client.chat.completions = completions
    monkeypatch.setattr(ai, "_get_client", lambda: client)
    assert ai.generate("social_post", "x") == "recovered"
    assert completions.calls == 3  # 1 initial + 2 retries


def test_model_key_selects_model(monkeypatch):
    captured = {}

    class CapturingCompletions:
        def create(self, **kwargs):
            captured["model"] = kwargs["model"]
            return FakeResp("ok")

    client = FakeClient()
    client.chat.completions = CapturingCompletions()
    monkeypatch.setattr(ai, "_get_client", lambda: client)
    ai.generate("social_post", "x", model_key="llama")
    assert captured["model"] == ai.MODELS["llama"]


def test_none_content_raises_runtime_error(monkeypatch):
    # Groq can return content=None (e.g. content_filter); must not crash with AttributeError.
    monkeypatch.setattr(ai, "_get_client", lambda: make_client(content=None))
    with pytest.raises(RuntimeError) as exc_info:
        ai.generate("social_post", "x")
    assert "empty" in exc_info.value.args[0].lower()


def test_tone_and_length_reach_system_prompt(monkeypatch):
    captured = {}

    class CapturingCompletions:
        def create(self, **kwargs):
            captured["system"] = kwargs["messages"][0]["content"]
            captured["max_tokens"] = kwargs["max_tokens"]
            return FakeResp("ok")

    client = FakeClient()
    client.chat.completions = CapturingCompletions()
    monkeypatch.setattr(ai, "_get_client", lambda: client)
    ai.generate("social_post", "x", tone="funny", length="short")
    assert "funny" in captured["system"].lower()
    assert captured["max_tokens"] == ai.LENGTHS["short"][1]

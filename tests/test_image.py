"""Tests for bot/image.py — monkeypatches httpx.get."""
import pytest
import httpx

from bot import image


# ---------------------------------------------------------------------------
# Fake response
# ---------------------------------------------------------------------------

class FakeResponse:
    def __init__(self, content: bytes = b"JPEGDATA", raise_on_status: bool = False):
        self.content = content
        self._raise = raise_on_status

    def raise_for_status(self):
        if self._raise:
            raise httpx.HTTPStatusError(
                "error", request=None, response=None  # type: ignore[arg-type]
            )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_generate_image_returns_bytes(monkeypatch):
    monkeypatch.setattr(image.httpx, "get", lambda url, timeout: FakeResponse(b"JPEGDATA"))
    result = image.generate_image("a cat")
    assert result == b"JPEGDATA"


def test_generate_image_raises_on_http_error(monkeypatch):
    monkeypatch.setattr(
        image.httpx, "get", lambda url, timeout: FakeResponse(raise_on_status=True)
    )
    with pytest.raises(RuntimeError) as exc_info:
        image.generate_image("a cat")
    assert "Image generation failed" in exc_info.value.args[0]

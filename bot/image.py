"""Pollinations.ai image generation."""
import logging
import urllib.parse

import httpx

logger = logging.getLogger(__name__)


def generate_image(prompt: str, width: int = 1024, height: int = 1024) -> bytes:
    """Return JPEG bytes from Pollinations for the given prompt and dimensions."""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"
    try:
        resp = httpx.get(url, timeout=60)
        resp.raise_for_status()
        return resp.content
    except Exception as exc:
        logger.exception("Pollinations image generation failed")
        raise RuntimeError("⚠️ Image generation failed. Please try again.") from exc

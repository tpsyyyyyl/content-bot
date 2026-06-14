"""Pollinations.ai image generation."""
import urllib.parse

import httpx


def generate_image(prompt: str) -> bytes:
    """Return JPEG bytes from Pollinations for the given prompt."""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
    try:
        resp = httpx.get(url, timeout=60)
        resp.raise_for_status()
        return resp.content
    except Exception as exc:
        raise RuntimeError("⚠️ Image generation failed. Please try again.") from exc

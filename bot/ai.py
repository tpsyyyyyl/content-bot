"""Groq-backed text generation: content, translation, summarization."""
import logging
import os
import time

from groq import Groq

from .config import CONTENT_TYPES, LANGUAGES, LENGTHS, TONES

logger = logging.getLogger(__name__)

MODELS = {
    "gpt-oss": "openai/gpt-oss-120b",
    "llama": "llama-3.3-70b-versatile",
}
DEFAULT_MODEL_KEY = os.getenv("GROQ_MODEL", "gpt-oss")

# Rate-limit retry policy: sleep these many seconds between attempts.
_RETRY_BACKOFF = (1, 2)

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        _client = Groq(api_key=api_key)
    return _client


def _is_rate_limit(exc: Exception) -> bool:
    text = str(exc).lower()
    return "rate_limit" in text or "429" in text


def _chat(system: str, user: str, *, max_tokens: int = 2048, model_key: str | None = None) -> str:
    """Single chat completion with retry on rate-limit and friendly errors."""
    model = MODELS.get(model_key or DEFAULT_MODEL_KEY, MODELS["gpt-oss"])
    last_exc: Exception | None = None

    for attempt in range(len(_RETRY_BACKOFF) + 1):
        try:
            resp = _get_client().chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.7,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # noqa: BLE001 — surface a clean message to the user
            last_exc = exc
            if _is_rate_limit(exc) and attempt < len(_RETRY_BACKOFF):
                delay = _RETRY_BACKOFF[attempt]
                logger.warning("Groq rate-limited, retrying in %ss (attempt %s)", delay, attempt + 1)
                time.sleep(delay)
                continue
            break
        else:
            content = (resp.choices[0].message.content or "").strip()
            if not content:
                raise RuntimeError("⚠️ The AI returned an empty response. Please try again.")
            return content

    logger.exception("Groq request failed", exc_info=last_exc)
    if last_exc is not None and _is_rate_limit(last_exc):
        raise RuntimeError("⏳ The AI is rate-limited right now. Try again in a moment.") from last_exc
    raise RuntimeError("⚠️ The AI service failed. Please try again.") from last_exc


def generate(
    content_type: str,
    prompt: str,
    *,
    tone: str | None = None,
    length: str | None = None,
    model_key: str | None = None,
) -> str:
    """Generate marketing content of a given type from a short brief."""
    _, instruction = CONTENT_TYPES[content_type]
    parts = ["You are an expert marketing copywriter.", instruction]
    if tone in TONES:
        parts.append(f"Use a {TONES[tone]} tone.")
    max_tokens = 2048
    if length in LENGTHS:
        label, max_tokens = LENGTHS[length]
        parts.append(f"Target length: {label}.")
    parts.append("Reply with the content only — no preamble, no explanations.")
    system = " ".join(parts)
    return _chat(system, prompt, max_tokens=max_tokens, model_key=model_key)


def translate(lang_code: str, text: str, *, model_key: str | None = None) -> str:
    """Translate text into the target language."""
    language = LANGUAGES[lang_code].split(" ", 1)[-1]  # strip the flag emoji
    system = (
        f"You are a professional translator. Translate the user's text into {language}. "
        "Preserve tone and meaning. Reply with the translation only."
    )
    return _chat(system, text, model_key=model_key)


def summarize(text: str, *, model_key: str | None = None) -> str:
    """Summarize text into a short paragraph plus key points."""
    system = (
        "You are a skilled editor. Summarize the user's text. "
        "Reply with a one-paragraph summary, then a blank line, "
        "then 3-5 key points as a bulleted list starting with '• '."
    )
    return _chat(system, text, model_key=model_key)

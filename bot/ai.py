"""Groq-backed text generation: content, translation, summarization."""
import os

from groq import Groq

from .config import CONTENT_TYPES, LANGUAGES

MODELS = {
    "gpt-oss": "openai/gpt-oss-120b",
    "llama": "llama-3.3-70b-versatile",
}
DEFAULT_MODEL_KEY = os.getenv("GROQ_MODEL", "gpt-oss")

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        _client = Groq(api_key=api_key)
    return _client


def _chat(system: str, user: str, *, max_tokens: int = 2048) -> str:
    """Single chat completion with friendly error handling."""
    model = MODELS.get(DEFAULT_MODEL_KEY, MODELS["gpt-oss"])
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
        return resp.choices[0].message.content.strip()
    except Exception as exc:  # noqa: BLE001 — surface a clean message to the user
        text = str(exc).lower()
        if "rate_limit" in text or "429" in text:
            raise RuntimeError("⏳ The AI is rate-limited right now. Try again in a moment.") from exc
        raise RuntimeError("⚠️ The AI service failed. Please try again.") from exc


def generate(content_type: str, prompt: str) -> str:
    """Generate marketing content of a given type from a short brief."""
    _, instruction = CONTENT_TYPES[content_type]
    system = (
        "You are an expert marketing copywriter. "
        f"{instruction} "
        "Reply with the content only — no preamble, no explanations."
    )
    return _chat(system, prompt)


def translate(lang_code: str, text: str) -> str:
    """Translate text into the target language."""
    language = LANGUAGES[lang_code].split(" ", 1)[-1]  # strip the flag emoji
    system = (
        f"You are a professional translator. Translate the user's text into {language}. "
        "Preserve tone and meaning. Reply with the translation only."
    )
    return _chat(system, text)


def summarize(text: str) -> str:
    """Summarize text into a short paragraph plus key points."""
    system = (
        "You are a skilled editor. Summarize the user's text. "
        "Reply with a one-paragraph summary, then a blank line, "
        "then 3-5 key points as a bulleted list starting with '• '."
    )
    return _chat(system, text)

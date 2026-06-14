"""Helper for sending text that may exceed Telegram's 4096-char message limit."""
from ..config import TELEGRAM_MSG_LIMIT


def _split(text: str, limit: int = TELEGRAM_MSG_LIMIT) -> list[str]:
    """Split text into <=limit chunks, preferring line boundaries."""
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        # A single oversized line is hard-split.
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > limit:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks or [""]


async def reply_chunks(message, text: str, reply_markup=None) -> None:
    """Reply with text split across messages; markup goes on the last chunk only."""
    chunks = _split(text)
    for i, chunk in enumerate(chunks):
        markup = reply_markup if i == len(chunks) - 1 else None
        await message.reply_text(chunk, reply_markup=markup)

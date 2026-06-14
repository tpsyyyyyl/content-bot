"""Central configuration: env vars and shared constants."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env sitting next to the project root, regardless of CWD.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/bot.db")

# Free-tier daily limit per user (admin is exempt).
DAILY_LIMIT = 10
# How many recent generations /history shows.
HISTORY_LIMIT = 50

# Content types for /generate: key -> (label, prompt instruction).
CONTENT_TYPES = {
    "social_post": (
        "📱 Social post",
        "Write an engaging social media post. Use a hook, a clear value, and 2-3 relevant hashtags.",
    ),
    "email": (
        "✉️ Email",
        "Write a concise, professional marketing email with a subject line and a clear call to action.",
    ),
    "ad_copy": (
        "📢 Ad copy",
        "Write short, punchy advertising copy that drives clicks. Lead with the benefit.",
    ),
    "blog_intro": (
        "📝 Blog intro",
        "Write a compelling blog post introduction (3-4 sentences) that hooks the reader.",
    ),
}

# Target languages for /translate: code -> label.
LANGUAGES = {
    "en": "🇬🇧 English",
    "uk": "🇺🇦 Ukrainian",
    "ru": "🇷🇺 Russian",
    "de": "🇩🇪 German",
    "pl": "🇵🇱 Polish",
    "es": "🇪🇸 Spanish",
}

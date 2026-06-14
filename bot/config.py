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
    "linkedin_post": (
        "💼 LinkedIn post",
        "Write a professional LinkedIn post: a strong opening line, a short insight or story, "
        "and a closing question or takeaway. Use line breaks for readability.",
    ),
    "product_desc": (
        "🛍️ Product description",
        "Write a persuasive e-commerce product description. Lead with the key benefit, "
        "cover 2-3 features, and end with a short call to action.",
    ),
}

# Tone options for /generate: key -> label shown in the prompt.
TONES = {
    "professional": "professional",
    "casual": "casual",
    "funny": "funny",
}

# Length options for /generate: key -> (label, max_tokens).
LENGTHS = {
    "short": ("Short (~50 words)", 512),
    "long": ("Long (~200 words)", 2048),
}

# Image aspect options for /image: key -> (label, width, height).
IMAGE_RATIOS = {
    "square": ("⬜ Square", 1024, 1024),
    "landscape": ("🖼️ Landscape", 1280, 768),
    "portrait": ("📱 Portrait", 768, 1280),
}

# Telegram hard limit on a single text message.
TELEGRAM_MSG_LIMIT = 4096

# Target languages for /translate: code -> label.
LANGUAGES = {
    "en": "🇬🇧 English",
    "uk": "🇺🇦 Ukrainian",
    "ru": "🇷🇺 Russian",
    "de": "🇩🇪 German",
    "pl": "🇵🇱 Polish",
    "es": "🇪🇸 Spanish",
}

"""Basic command handlers: /start and /help."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register user and send a welcome message."""
    u = update.effective_user
    db.get_or_create_user(u.id, u.username)
    await update.message.reply_text(
        f"👋 Hey {u.first_name}! I'm your AI content assistant.\n\n"
        "✨ Here's what I can do:\n"
        "  /generate — create social posts, emails, ads, blog intros\n"
        "  /translate — translate text into 6 languages\n"
        "  /summarize — condense long text into key points\n"
        "  /image — generate an image from a description\n"
        "  /history — browse your recent generations\n"
        "  /templates — reuse your saved content\n\n"
        "Type /help for the full command list. Let's create something! 🚀"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a concise list of all commands."""
    await update.message.reply_text(
        "📋 *Commands:*\n\n"
        "/generate — pick a content type and get AI-written copy\n"
        "/translate — translate your text into another language\n"
        "/summarize — summarize long text + bullet points\n"
        "/image — generate an image from a text prompt\n"
        "/history — see your last 10 generations\n"
        "/templates — list and reuse saved templates\n"
        "/stats — admin: user & generation stats\n"
        "/top — admin: top 5 users by usage",
        parse_mode="Markdown",
    )

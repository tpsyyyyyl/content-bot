"""Basic command handlers: /start and /help."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import db
from ..config import ADMIN_TELEGRAM_ID
from ..keyboards import main_menu_kb


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register user, send a welcome message and show the main menu keyboard."""
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
        "  /templates — reuse your saved content\n"
        "  /settings — switch the AI model\n\n"
        "Tap a button below, or /cancel anytime to stop. Type /help for the full list. Let's create something! 🚀",
        reply_markup=main_menu_kb(is_admin=u.id == ADMIN_TELEGRAM_ID),
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
        "/settings — switch the AI model (gpt-oss / llama)\n"
        "/cancel — stop the current action\n"
        "/stats — admin: user & generation stats\n"
        "/top — admin: top 5 users by usage",
        parse_mode="Markdown",
    )

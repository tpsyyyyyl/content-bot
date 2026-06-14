"""Admin-only command handlers: /stats and /top."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import db
from ..config import ADMIN_TELEGRAM_ID


def _is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_TELEGRAM_ID


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stats — show total users and generations (admin only)."""
    if not _is_admin(update):
        await update.message.reply_text("🔒 Admin only.")
        return
    data = db.stats()
    await update.message.reply_text(f"👥 Users: {data['users']}\n✨ Generations: {data['generations']}")


async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/top — show top 5 users by usage (admin only)."""
    if not _is_admin(update):
        await update.message.reply_text("🔒 Admin only.")
        return
    rows = db.top_users(5)
    if not rows:
        await update.message.reply_text("📊 No usage data yet.")
        return
    lines = [f"{i}. {row['username'] or 'unknown'} — {row['usage_count']}" for i, row in enumerate(rows, 1)]
    await update.message.reply_text("🏆 *Top users:*\n\n" + "\n".join(lines), parse_mode="Markdown")

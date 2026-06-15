"""Admin-only command handlers: /stats and /top."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import db, i18n
from ..config import ADMIN_TELEGRAM_ID
from ._common import identify, user_lang


def _is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_TELEGRAM_ID


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stats — show total users and generations (admin only)."""
    _, user_id = identify(update)
    lang = user_lang(user_id)
    if not _is_admin(update):
        await update.message.reply_text(i18n.t("admin_only", lang))
        return
    data = db.stats()
    await update.message.reply_text(
        i18n.t("stats_message", lang, users=data["users"], generations=data["generations"])
    )


async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/top — show top 5 users by usage (admin only)."""
    _, user_id = identify(update)
    lang = user_lang(user_id)
    if not _is_admin(update):
        await update.message.reply_text(i18n.t("admin_only", lang))
        return
    rows = db.top_users(5)
    if not rows:
        await update.message.reply_text(i18n.t("top_empty", lang))
        return
    lines = [f"{i}. {row['username'] or 'unknown'} — {row['usage_count']}" for i, row in enumerate(rows, 1)]
    await update.message.reply_text(i18n.t("top_header", lang) + "\n\n" + "\n".join(lines))

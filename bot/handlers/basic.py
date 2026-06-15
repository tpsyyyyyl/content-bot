"""Basic command handlers: /start and /help."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import db, i18n
from ..config import ADMIN_TELEGRAM_ID
from ..keyboards import language_select_kb, main_menu_kb
from ._common import identify, user_lang


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register user; show language picker for new users, welcome for existing."""
    tg_id, user_id = identify(update)
    lang = db.get_lang(user_id)
    if lang is None:
        # New user — show bilingual language-selection screen
        await update.message.reply_text(
            i18n.t("choose_language", i18n.DEFAULT_LANG),
            reply_markup=language_select_kb(),
        )
    else:
        await update.message.reply_text(
            i18n.t("welcome", lang, name=update.effective_user.first_name),
            reply_markup=main_menu_kb(is_admin=tg_id == ADMIN_TELEGRAM_ID, lang=lang),
        )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a concise list of all commands."""
    _, user_id = identify(update)
    lang = user_lang(user_id)
    await update.message.reply_text(
        i18n.t("help", lang),
        parse_mode="Markdown",
    )

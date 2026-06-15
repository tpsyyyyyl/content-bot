"""Settings handler: /settings — per-user AI model and language choice."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import ai, db, i18n
from ..config import ADMIN_TELEGRAM_ID
from ..keyboards import main_menu_kb, settings_kb
from ._common import identify, user_lang


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/settings — show current model + language and let the user switch both."""
    tg_id, user_id = identify(update)
    lang = user_lang(user_id)
    current_model = db.get_model_key(user_id, ai.DEFAULT_MODEL_KEY)
    current_lang = db.get_lang(user_id) or i18n.DEFAULT_LANG
    await update.message.reply_text(
        i18n.t("settings_prompt", lang, model=current_model),
        reply_markup=settings_kb(ai.MODELS, current_model, current_lang, lang),
        parse_mode="Markdown",
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Persist chosen model from a setmodel:<key> tap; rebuild settings screen."""
    query = update.callback_query
    await query.answer()
    key = query.data[len("setmodel:"):]
    if key not in ai.MODELS:
        return
    tg_id, user_id = identify(update)
    db.set_model_key(user_id, key)
    lang = user_lang(user_id)
    current_lang = db.get_lang(user_id) or i18n.DEFAULT_LANG
    await query.edit_message_text(
        i18n.t("settings_prompt", lang, model=key),
        reply_markup=settings_kb(ai.MODELS, key, current_lang, lang),
        parse_mode="Markdown",
    )


async def on_setlang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setlang:<code> — set language; show welcome if first time, settings if change."""
    query = update.callback_query
    await query.answer()
    code = query.data.split(":")[1]
    if code not in i18n.UI_LANGUAGES:
        return
    tg_id, user_id = identify(update)
    prev = db.get_lang(user_id)
    db.set_lang(user_id, code)
    if prev is None:
        # First-time language pick from /start flow
        text = i18n.t("language_set", code, lang_name=i18n.UI_LANGUAGES[code])
        await query.edit_message_text(text)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=i18n.t("welcome", code, name=update.effective_user.first_name),
            reply_markup=main_menu_kb(is_admin=tg_id == ADMIN_TELEGRAM_ID, lang=code),
        )
    else:
        # Change from /settings — rebuild settings screen in the new language
        current_model = db.get_model_key(user_id, ai.DEFAULT_MODEL_KEY)
        await query.edit_message_text(
            i18n.t("settings_prompt", code, model=current_model),
            reply_markup=settings_kb(ai.MODELS, current_model, code, code),
            parse_mode="Markdown",
        )

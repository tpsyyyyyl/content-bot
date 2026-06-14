"""Settings handler: /settings — per-user AI model choice."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import ai, db
from ..keyboards import model_kb
from ._common import identify


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/settings — show current model and let the user switch."""
    _, user_id = identify(update)
    current = db.get_model_key(user_id, ai.DEFAULT_MODEL_KEY)
    await update.message.reply_text(
        f"🔧 Current AI model: *{current}*\nPick one:",
        reply_markup=model_kb(ai.MODELS, current),
        parse_mode="Markdown",
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Persist the chosen model from a setmodel:<key> tap."""
    query = update.callback_query
    await query.answer()
    key = query.data[len("setmodel:"):]
    if key not in ai.MODELS:
        return
    _, user_id = identify(update)
    db.set_model_key(user_id, key)
    await query.edit_message_text(f"✅ Model set to *{key}*.", parse_mode="Markdown")

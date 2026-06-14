"""Core feature handlers: /generate, /translate, /summarize, /image, text router."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import ai, db, image
from ..config import DAILY_LIMIT
from ..keyboards import content_types_kb, languages_kb, save_template_kb


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _identify(update: Update) -> tuple[int, int]:
    """Return (telegram_id, internal user_id), registering the user if needed."""
    u = update.effective_user
    user_id = db.get_or_create_user(u.id, u.username)
    return u.id, user_id


async def _ensure_quota(update: Update, telegram_id: int, user_id: int) -> bool:
    """Reply and return False if the daily limit is exhausted."""
    rem = db.remaining_quota(telegram_id, user_id)
    if rem is not None and rem <= 0:
        await update.effective_message.reply_text(
            f"⏳ Daily limit reached ({DAILY_LIMIT}/day). Try again tomorrow."
        )
        return False
    return True


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def generate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/generate — show content-type picker."""
    _identify(update)
    await update.message.reply_text("Choose a content type:", reply_markup=content_types_kb())


async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/translate — show language picker."""
    _identify(update)
    await update.message.reply_text("Choose a target language:", reply_markup=languages_kb())


async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/summarize — ask user for the text to summarize."""
    _identify(update)
    context.user_data["pending"] = {"action": "summarize"}
    await update.message.reply_text("📝 Send the text you want summarized.")


async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/image — generate immediately if args given, otherwise ask for a prompt."""
    telegram_id, user_id = _identify(update)
    if context.args:
        prompt = " ".join(context.args)
        if not await _ensure_quota(update, telegram_id, user_id):
            return
        await update.message.reply_chat_action("upload_photo")
        try:
            photo_bytes = image.generate_image(prompt)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, "image", prompt, "<image>")
        await update.message.reply_photo(photo=photo_bytes, caption=prompt[:200])
    else:
        context.user_data["pending"] = {"action": "image"}
        await update.message.reply_text("🎨 Send a prompt describing the image.")


# ---------------------------------------------------------------------------
# Callback handler for gen: and tr: prefixes
# ---------------------------------------------------------------------------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle gen:<key> and tr:<code> inline button taps."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("gen:"):
        key = data[len("gen:"):]
        context.user_data["pending"] = {"action": "generate", "content_type": key}
        await query.edit_message_text("✏️ Now send your brief / topic.")

    elif data.startswith("tr:"):
        code = data[len("tr:"):]
        context.user_data["pending"] = {"action": "translate", "lang": code}
        await query.edit_message_text("💬 Send the text you want translated.")


# ---------------------------------------------------------------------------
# Text router — the single MessageHandler for plain text
# ---------------------------------------------------------------------------

async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispatch incoming plain text based on pending action."""
    pending = context.user_data.pop("pending", None)
    if not pending:
        await update.message.reply_text("ℹ️ Pick a command first — see /help.")
        return

    action = pending["action"]
    text = update.message.text

    # --- name_template doesn't need quota ---
    if action == "name_template":
        telegram_id, user_id = _identify(update)
        db.save_template(
            user_id,
            name=text.strip(),
            kind=pending["type"],
            content=pending["content"],
        )
        await update.message.reply_text(f"✅ Saved template '{text.strip()}'.")
        return

    telegram_id, user_id = _identify(update)
    if not await _ensure_quota(update, telegram_id, user_id):
        return

    await update.message.reply_chat_action("typing")

    if action == "generate":
        kind = pending["content_type"]
        try:
            result = ai.generate(kind, text)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, kind, text, result)
        context.user_data["last"] = {"type": kind, "content": result}
        await update.message.reply_text(result, reply_markup=save_template_kb())

    elif action == "translate":
        kind = "translate"
        try:
            result = ai.translate(pending["lang"], text)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, kind, text, result)
        context.user_data["last"] = {"type": kind, "content": result}
        await update.message.reply_text(result, reply_markup=save_template_kb())

    elif action == "summarize":
        kind = "summarize"
        try:
            result = ai.summarize(text)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, kind, text, result)
        context.user_data["last"] = {"type": kind, "content": result}
        await update.message.reply_text(result, reply_markup=save_template_kb())

    elif action == "image":
        await update.message.reply_chat_action("upload_photo")
        try:
            photo_bytes = image.generate_image(text)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, "image", text, "<image>")
        await update.message.reply_photo(photo=photo_bytes, caption=text[:200])

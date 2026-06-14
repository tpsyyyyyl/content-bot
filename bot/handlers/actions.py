"""Core feature handlers: /generate, /translate, /summarize, /image, text router."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from .. import ai, db, image
from ..config import ADMIN_TELEGRAM_ID, DAILY_LIMIT, IMAGE_RATIOS
from ..keyboards import (
    content_types_kb,
    image_ratio_kb,
    languages_kb,
    length_kb,
    main_menu_kb,
    result_kb,
    tone_kb,
)
from ._reply import reply_chunks

logger = logging.getLogger(__name__)


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


def _kind_of(action: str, params: dict) -> str:
    """Map an action to the db history `type` value."""
    if action == "generate":
        return params["content_type"]
    return action  # "translate" / "summarize"


def _produce(action: str, params: dict, text: str, model_key: str | None) -> str:
    """Run the AI call for a text action and return the result."""
    if action == "generate":
        return ai.generate(
            params["content_type"],
            text,
            tone=params.get("tone"),
            length=params.get("length"),
            model_key=model_key,
        )
    if action == "translate":
        return ai.translate(params["lang"], text, model_key=model_key)
    return ai.summarize(text, model_key=model_key)


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
    """/image — generate immediately (square) if args given, else show ratio picker."""
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
        await update.message.reply_text("🎨 Choose an image format:", reply_markup=image_ratio_kb())


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/cancel — drop any pending action and show the main menu."""
    context.user_data.pop("pending", None)
    is_admin = update.effective_user.id == ADMIN_TELEGRAM_ID
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu_kb(is_admin=is_admin))


# ---------------------------------------------------------------------------
# Callback handler for gen:/gtone:/glen:/tr:/imgr:/regen: prefixes
# ---------------------------------------------------------------------------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button taps for the generate/translate/image flows."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("gen:"):
        content_type = data[len("gen:"):]
        await query.edit_message_text("Choose a tone:", reply_markup=tone_kb(content_type))

    elif data.startswith("gtone:"):
        _, content_type, tone = data.split(":", 2)
        await query.edit_message_text("Choose a length:", reply_markup=length_kb(content_type, tone))

    elif data.startswith("glen:"):
        _, content_type, tone, length = data.split(":", 3)
        context.user_data["pending"] = {
            "action": "generate",
            "content_type": content_type,
            "tone": tone,
            "length": length,
        }
        await query.edit_message_text("✏️ Now send your brief / topic.")

    elif data.startswith("tr:"):
        code = data[len("tr:"):]
        context.user_data["pending"] = {"action": "translate", "lang": code}
        await query.edit_message_text("💬 Send the text you want translated.")

    elif data.startswith("imgr:"):
        ratio = data[len("imgr:"):]
        context.user_data["pending"] = {"action": "image", "ratio": ratio}
        await query.edit_message_text("🎨 Send a prompt describing the image.")

    elif data.startswith("regen:"):
        await _regenerate(update, context)


async def _regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Re-run the last text generation with the same inputs."""
    query = update.callback_query
    last = context.user_data.get("last")
    if not last or last.get("action") not in ("generate", "translate", "summarize"):
        await query.message.reply_text("⚠️ Nothing to regenerate yet.")
        return

    telegram_id, user_id = _identify(update)
    if not await _ensure_quota(update, telegram_id, user_id):
        return

    await query.message.reply_chat_action("typing")
    model_key = db.get_model_key(user_id, ai.DEFAULT_MODEL_KEY)
    try:
        result = _produce(last["action"], last, last["input"], model_key)
    except RuntimeError as exc:
        await query.message.reply_text(str(exc))
        return

    db.record_generation(user_id, last["kind"], last["input"], result)
    last["result"] = result
    await reply_chunks(query.message, result, result_kb())


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

    if action in ("generate", "translate", "summarize"):
        await update.message.reply_chat_action("typing")
        model_key = db.get_model_key(user_id, ai.DEFAULT_MODEL_KEY)
        try:
            result = _produce(action, pending, text, model_key)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        kind = _kind_of(action, pending)
        db.record_generation(user_id, kind, text, result)
        context.user_data["last"] = {
            "action": action,
            "kind": kind,
            "input": text,
            "result": result,
            "content_type": pending.get("content_type"),
            "tone": pending.get("tone"),
            "length": pending.get("length"),
            "lang": pending.get("lang"),
        }
        await reply_chunks(update.message, result, result_kb())

    elif action == "image":
        ratio = pending.get("ratio", "square")
        _, width, height = IMAGE_RATIOS.get(ratio, IMAGE_RATIOS["square"])
        await update.message.reply_chat_action("upload_photo")
        try:
            photo_bytes = image.generate_image(text, width, height)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, "image", text, "<image>")
        await update.message.reply_photo(photo=photo_bytes, caption=text[:200])

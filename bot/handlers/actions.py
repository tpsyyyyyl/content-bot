"""Core feature handlers: /generate, /translate, /summarize, /image, text router."""
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from .. import ai, db, i18n, image
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
from ._common import identify, user_lang
from ._reply import reply_chunks


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

async def _ensure_quota(update: Update, telegram_id: int, user_id: int, lang: str) -> bool:
    """Reply and return False if the daily limit is exhausted."""
    rem = db.remaining_quota(telegram_id, user_id)
    if rem is not None and rem <= 0:
        await update.effective_message.reply_text(
            i18n.t("daily_limit_reached", lang, limit=DAILY_LIMIT)
        )
        return False
    return True


def _kind_of(action: str, params: dict) -> str:
    """Map an action to the db history `type` value."""
    if action == "generate":
        return params["content_type"]
    return action  # "translate" / "summarize"


def _produce(action: str, params: dict, text: str, model_key: str | None) -> str:
    """Run the (blocking) AI call for a text action and return the result."""
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
    _, user_id = identify(update)
    lang = user_lang(user_id)
    await update.message.reply_text(
        i18n.t("choose_content_type", lang),
        reply_markup=content_types_kb(lang),
    )


async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/translate — show language picker."""
    _, user_id = identify(update)
    lang = user_lang(user_id)
    await update.message.reply_text(
        i18n.t("choose_target_language", lang),
        reply_markup=languages_kb(lang),
    )


async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/summarize — ask user for the text to summarize."""
    _, user_id = identify(update)
    lang = user_lang(user_id)
    context.user_data["pending"] = {"action": "summarize"}
    await update.message.reply_text(i18n.t("send_text_to_summarize", lang))


async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/image — generate immediately (square) if args given, else show ratio picker."""
    context.user_data.pop("pending", None)
    telegram_id, user_id = identify(update)
    lang = user_lang(user_id)
    if context.args:
        prompt = " ".join(context.args)
        if not await _ensure_quota(update, telegram_id, user_id, lang):
            return
        await update.message.reply_chat_action("upload_photo")
        try:
            photo_bytes = await asyncio.to_thread(image.generate_image, prompt)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, "image", prompt, "<image>")
        await update.message.reply_photo(photo=photo_bytes, caption=prompt[:200])
    else:
        await update.message.reply_text(
            i18n.t("choose_image_format", lang),
            reply_markup=image_ratio_kb(lang),
        )


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/cancel — drop any pending action and show the main menu."""
    context.user_data.pop("pending", None)
    tg_id = update.effective_user.id
    _, user_id = identify(update)
    lang = user_lang(user_id)
    is_admin = tg_id == ADMIN_TELEGRAM_ID
    await update.message.reply_text(
        i18n.t("cancelled", lang),
        reply_markup=main_menu_kb(is_admin=is_admin, lang=lang),
    )


# ---------------------------------------------------------------------------
# Callback handler for gen:/gtone:/glen:/tr:/imgr:/regen: prefixes
# ---------------------------------------------------------------------------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button taps for the generate/translate/image flows."""
    query = update.callback_query
    await query.answer()
    data = query.data
    _, user_id = identify(update)
    lang = user_lang(user_id)

    if data.startswith("gen:"):
        content_type = data[len("gen:"):]
        await query.edit_message_text(
            i18n.t("choose_tone", lang),
            reply_markup=tone_kb(content_type, lang),
        )

    elif data.startswith("gtone:"):
        parts = data.split(":")
        if len(parts) != 3:
            return
        _, content_type, tone = parts
        await query.edit_message_text(
            i18n.t("choose_length", lang),
            reply_markup=length_kb(content_type, tone, lang),
        )

    elif data.startswith("glen:"):
        parts = data.split(":")
        if len(parts) != 4:
            return
        _, content_type, tone, length = parts
        context.user_data["pending"] = {
            "action": "generate",
            "content_type": content_type,
            "tone": tone,
            "length": length,
        }
        await query.edit_message_text(i18n.t("send_brief", lang))

    elif data.startswith("tr:"):
        code = data[len("tr:"):]
        context.user_data["pending"] = {"action": "translate", "lang": code}
        await query.edit_message_text(i18n.t("send_text_to_translate", lang))

    elif data.startswith("imgr:"):
        ratio = data[len("imgr:"):]
        context.user_data["pending"] = {"action": "image", "ratio": ratio}
        await query.edit_message_text(i18n.t("send_image_prompt", lang))

    elif data.startswith("regen:"):
        await _regenerate(update, context)


async def _regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Re-run the last text generation with the same inputs."""
    query = update.callback_query
    last = context.user_data.get("last")
    _, user_id = identify(update)
    lang = user_lang(user_id)
    if not last or last.get("action") not in ("generate", "translate", "summarize"):
        await query.message.reply_text(i18n.t("nothing_to_regenerate", lang))
        return

    telegram_id = update.effective_user.id
    if not await _ensure_quota(update, telegram_id, user_id, lang):
        return

    await query.message.reply_chat_action("typing")
    model_key = db.get_model_key(user_id, ai.DEFAULT_MODEL_KEY)
    try:
        result = await asyncio.to_thread(_produce, last["action"], last, last["input"], model_key)
    except RuntimeError as exc:
        await query.message.reply_text(str(exc))
        return

    db.record_generation(user_id, last["kind"], last["input"], result)
    last["result"] = result
    await reply_chunks(query.message, result, result_kb(lang))


# ---------------------------------------------------------------------------
# Text router — the single MessageHandler for plain text
# ---------------------------------------------------------------------------

async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispatch incoming plain text based on pending action."""
    pending = context.user_data.pop("pending", None)
    if not pending:
        _, user_id = identify(update)
        lang = user_lang(user_id)
        await update.message.reply_text(i18n.t("no_pending_action", lang))
        return

    action = pending["action"]
    text = update.message.text

    # --- name_template doesn't need quota ---
    if action == "name_template":
        telegram_id, user_id = identify(update)
        lang = user_lang(user_id)
        db.save_template(
            user_id,
            name=text.strip(),
            kind=pending["type"],
            content=pending["content"],
        )
        await update.message.reply_text(i18n.t("template_saved", lang, name=text.strip()))
        return

    telegram_id, user_id = identify(update)
    lang = user_lang(user_id)
    if not await _ensure_quota(update, telegram_id, user_id, lang):
        return

    if action in ("generate", "translate", "summarize"):
        await update.message.reply_chat_action("typing")
        model_key = db.get_model_key(user_id, ai.DEFAULT_MODEL_KEY)
        try:
            result = await asyncio.to_thread(_produce, action, pending, text, model_key)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        kind = _kind_of(action, pending)
        db.record_generation(user_id, kind, text, result)
        context.user_data["last"] = {**pending, "kind": kind, "input": text, "result": result}
        await reply_chunks(update.message, result, result_kb(lang))

    elif action == "image":
        ratio = pending.get("ratio", "square")
        _, width, height = IMAGE_RATIOS.get(ratio, IMAGE_RATIOS["square"])
        await update.message.reply_chat_action("upload_photo")
        try:
            photo_bytes = await asyncio.to_thread(image.generate_image, text, width, height)
        except RuntimeError as exc:
            await update.message.reply_text(str(exc))
            return
        db.record_generation(user_id, "image", text, "<image>")
        await update.message.reply_photo(photo=photo_bytes, caption=text[:200])

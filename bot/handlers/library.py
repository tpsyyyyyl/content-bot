"""Library handlers: /history, /templates, and tpluse/tplsave callbacks."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import db
from ..config import CONTENT_TYPES
from ..keyboards import templates_kb
from ._common import identify
from ._reply import reply_chunks

# Emoji for non-content-type history rows; content types derive from CONTENT_TYPES labels.
_EXTRA_EMOJI = {"translate": "🌐", "summarize": "📋", "image": "🖼️"}


def _emoji(type_key: str) -> str:
    """Emoji for a history row's type — single-sourced from CONTENT_TYPES labels."""
    if type_key in CONTENT_TYPES:
        return CONTENT_TYPES[type_key][0].split()[0]
    return _EXTRA_EMOJI.get(type_key, type_key)


async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/history — show last 10 generations."""
    _, user_id = identify(update)
    rows = db.get_history(user_id, 10)
    if not rows:
        await update.message.reply_text("📭 No history yet.")
        return

    lines = []
    for i, row in enumerate(rows, 1):
        emoji = _emoji(row["type"])
        prompt_short = (row["prompt"] or "")[:50]
        date_part = (row["created_at"] or "")[:10]
        lines.append(f"{i}. {emoji} · {prompt_short} · {date_part}")

    await update.message.reply_text("📜 Recent generations:\n\n" + "\n".join(lines))


async def templates_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/templates — list saved templates with reuse buttons."""
    _, user_id = identify(update)
    rows = db.list_templates(user_id)
    if not rows:
        await update.message.reply_text(
            "📂 No saved templates yet. Generate something, then tap 💾 Save as template."
        )
        return
    await update.message.reply_text("📁 Your templates:", reply_markup=templates_kb(rows))


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tplsave and tpluse:<id> inline button taps."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "tplsave":
        last = context.user_data.get("last")
        if not last:
            await query.message.reply_text("⚠️ Nothing to save yet.")
            return
        context.user_data["pending"] = {
            "action": "name_template",
            "type": last["kind"],
            "content": last["result"],
        }
        await query.message.reply_text("📝 Send a name for this template.")

    elif data.startswith("tpluse:"):
        template_id = int(data[len("tpluse:"):])
        _, user_id = identify(update)
        rows = db.list_templates(user_id)
        matched = next((r for r in rows if r["id"] == template_id), None)
        if matched is None:
            await query.message.reply_text("⚠️ Template not found.")
            return
        await reply_chunks(query.message, matched["content"])

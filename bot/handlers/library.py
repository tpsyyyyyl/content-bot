"""Library handlers: /history, /templates, and tpluse/tplsave callbacks."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import db
from ..keyboards import templates_kb

# Emoji map for content types shown in history.
_TYPE_EMOJI = {
    "social_post": "📱",
    "email": "✉️",
    "ad_copy": "📢",
    "blog_intro": "📝",
    "translate": "🌐",
    "summarize": "📋",
    "image": "🖼️",
}


def _identify(update: Update) -> tuple[int, int]:
    u = update.effective_user
    user_id = db.get_or_create_user(u.id, u.username)
    return u.id, user_id


async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/history — show last 10 generations."""
    _, user_id = _identify(update)
    rows = db.get_history(user_id, 10)
    if not rows:
        await update.message.reply_text("📭 No history yet.")
        return

    lines = []
    for i, row in enumerate(rows, 1):
        emoji = _TYPE_EMOJI.get(row["type"], row["type"])
        prompt_short = (row["prompt"] or "")[:50]
        date_part = (row["created_at"] or "")[:10]
        lines.append(f"{i}. {emoji} · {prompt_short} · {date_part}")

    await update.message.reply_text("📜 *Recent generations:*\n\n" + "\n".join(lines), parse_mode="Markdown")


async def templates_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/templates — list saved templates with reuse buttons."""
    _, user_id = _identify(update)
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
            "type": last["type"],
            "content": last["content"],
        }
        await query.message.reply_text("📝 Send a name for this template.")

    elif data.startswith("tpluse:"):
        template_id = int(data[len("tpluse:"):])
        _, user_id = _identify(update)
        rows = db.list_templates(user_id)
        matched = next((r for r in rows if r["id"] == template_id), None)
        if matched is None:
            await query.message.reply_text("⚠️ Template not found.")
            return
        await query.message.reply_text(matched["content"])

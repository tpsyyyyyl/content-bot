"""Keyboard builders for all bot menus (inline pickers + persistent main menu)."""
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from .config import CONTENT_TYPES, IMAGE_RATIOS, LANGUAGES, LENGTHS, TONES

# Persistent reply-keyboard button labels (also used by the menu router to
# map a tapped button back to its handler).
BTN_GENERATE = "✍️ Generate"
BTN_TRANSLATE = "🌐 Translate"
BTN_SUMMARIZE = "📝 Summarize"
BTN_IMAGE = "🎨 Image"
BTN_HISTORY = "🕘 History"
BTN_TEMPLATES = "📋 Templates"
BTN_HELP = "ℹ️ Help"
BTN_STATS = "📊 Stats"
BTN_TOP = "🏆 Top"


def main_menu_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Persistent reply keyboard with the main actions; admin gets Stats/Top."""
    rows = [
        [BTN_GENERATE, BTN_TRANSLATE, BTN_SUMMARIZE],
        [BTN_IMAGE, BTN_HISTORY, BTN_TEMPLATES],
        [BTN_HELP],
    ]
    if is_admin:
        rows.append([BTN_STATS, BTN_TOP])
    keyboard = [[KeyboardButton(label) for label in row] for row in rows]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def _rows(buttons: list[InlineKeyboardButton], per_row: int = 2) -> list[list[InlineKeyboardButton]]:
    return [buttons[i : i + per_row] for i in range(0, len(buttons), per_row)]


def content_types_kb() -> InlineKeyboardMarkup:
    """One button per CONTENT_TYPES entry, callback gen:<key>, 2 per row."""
    buttons = [
        InlineKeyboardButton(text=label, callback_data=f"gen:{key}")
        for key, (label, _) in CONTENT_TYPES.items()
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def languages_kb() -> InlineKeyboardMarkup:
    """One button per LANGUAGES entry, callback tr:<code>, 2 per row."""
    buttons = [
        InlineKeyboardButton(text=label, callback_data=f"tr:{code}")
        for code, label in LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def tone_kb(content_type: str) -> InlineKeyboardMarkup:
    """Tone picker shown after a content type, callback gtone:<type>:<tone>."""
    buttons = [
        InlineKeyboardButton(text=tone.capitalize(), callback_data=f"gtone:{content_type}:{key}")
        for key, tone in TONES.items()
    ]
    return InlineKeyboardMarkup(_rows(buttons, per_row=3))


def length_kb(content_type: str, tone: str) -> InlineKeyboardMarkup:
    """Length picker, callback glen:<type>:<tone>:<length>."""
    buttons = [
        InlineKeyboardButton(text=label, callback_data=f"glen:{content_type}:{tone}:{key}")
        for key, (label, _) in LENGTHS.items()
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def image_ratio_kb() -> InlineKeyboardMarkup:
    """Image aspect picker, callback imgr:<ratio>."""
    buttons = [
        InlineKeyboardButton(text=label, callback_data=f"imgr:{key}")
        for key, (label, _, _) in IMAGE_RATIOS.items()
    ]
    return InlineKeyboardMarkup(_rows(buttons, per_row=3))


def model_kb(models: dict, current: str) -> InlineKeyboardMarkup:
    """Model picker, callback setmodel:<key>; marks the active one."""
    buttons = [
        InlineKeyboardButton(
            text=f"{'✅ ' if key == current else ''}{key}",
            callback_data=f"setmodel:{key}",
        )
        for key in models
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def result_kb() -> InlineKeyboardMarkup:
    """Actions under a generated result: regenerate + save as template."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Regenerate", callback_data="regen:"),
                InlineKeyboardButton("💾 Save as template", callback_data="tplsave"),
            ]
        ]
    )


def templates_kb(rows) -> InlineKeyboardMarkup:
    """One '📋 <name>' button per template row, callback tpluse:<id>."""
    buttons = [
        InlineKeyboardButton(text=f"📋 {row['name']}", callback_data=f"tpluse:{row['id']}")
        for row in rows
    ]
    return InlineKeyboardMarkup(_rows(buttons))

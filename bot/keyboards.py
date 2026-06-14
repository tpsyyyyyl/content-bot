"""InlineKeyboardMarkup builders for all bot menus."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .config import CONTENT_TYPES, LANGUAGES


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


def save_template_kb() -> InlineKeyboardMarkup:
    """Single '💾 Save as template' button."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save as template", callback_data="tplsave")]])


def templates_kb(rows) -> InlineKeyboardMarkup:
    """One '📋 <name>' button per template row, callback tpluse:<id>."""
    buttons = [
        InlineKeyboardButton(text=f"📋 {row['name']}", callback_data=f"tpluse:{row['id']}")
        for row in rows
    ]
    return InlineKeyboardMarkup(_rows(buttons))

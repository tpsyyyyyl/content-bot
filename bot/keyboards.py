"""Keyboard builders for all bot menus (inline pickers + persistent main menu)."""
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from .config import CONTENT_TYPES, IMAGE_RATIOS, LANGUAGES, LENGTHS, TONES
from . import i18n

# action_key -> i18n string key (ordered so rows are predictable)
MENU_BUTTONS = {
    "generate": "btn_generate",
    "translate": "btn_translate",
    "summarize": "btn_summarize",
    "image": "btn_image",
    "history": "btn_history",
    "templates": "btn_templates",
    "help": "btn_help",
    "stats": "btn_stats",
    "top": "btn_top",
}

# Keep legacy BTN_* constants so old imports don't break during transition
BTN_GENERATE = i18n.t("btn_generate", "en")
BTN_TRANSLATE = i18n.t("btn_translate", "en")
BTN_SUMMARIZE = i18n.t("btn_summarize", "en")
BTN_IMAGE = i18n.t("btn_image", "en")
BTN_HISTORY = i18n.t("btn_history", "en")
BTN_TEMPLATES = i18n.t("btn_templates", "en")
BTN_HELP = i18n.t("btn_help", "en")
BTN_STATS = i18n.t("btn_stats", "en")
BTN_TOP = i18n.t("btn_top", "en")


def language_select_kb() -> InlineKeyboardMarkup:
    """Inline buttons to pick UI language (shown on first /start)."""
    buttons = [
        InlineKeyboardButton(label, callback_data=f"setlang:{code}")
        for code, label in i18n.UI_LANGUAGES.items()
    ]
    return InlineKeyboardMarkup([buttons])


def main_menu_kb(is_admin: bool = False, lang: str = i18n.DEFAULT_LANG) -> ReplyKeyboardMarkup:
    """Persistent reply keyboard; labels are localized to lang."""
    rows_keys = [
        ["generate", "translate", "summarize"],
        ["image", "history", "templates"],
        ["help"],
    ]
    keyboard = [
        [KeyboardButton(i18n.t(MENU_BUTTONS[k], lang)) for k in row]
        for row in rows_keys
    ]
    if is_admin:
        keyboard.append([
            KeyboardButton(i18n.t(MENU_BUTTONS["stats"], lang)),
            KeyboardButton(i18n.t(MENU_BUTTONS["top"], lang)),
        ])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def _rows(buttons: list[InlineKeyboardButton], per_row: int = 2) -> list[list[InlineKeyboardButton]]:
    return [buttons[i: i + per_row] for i in range(0, len(buttons), per_row)]


def content_types_kb(lang: str = i18n.DEFAULT_LANG) -> InlineKeyboardMarkup:
    """One button per CONTENT_TYPES entry, callback gen:<key>, 2 per row."""
    buttons = [
        InlineKeyboardButton(text=i18n.t(f"ct_{key}", lang), callback_data=f"gen:{key}")
        for key in CONTENT_TYPES
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def languages_kb(lang: str = i18n.DEFAULT_LANG) -> InlineKeyboardMarkup:
    """One button per LANGUAGES entry, callback tr:<code>, 2 per row."""
    buttons = [
        InlineKeyboardButton(text=i18n.t(f"lang_{code}", lang), callback_data=f"tr:{code}")
        for code in LANGUAGES
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def tone_kb(content_type: str, lang: str = i18n.DEFAULT_LANG) -> InlineKeyboardMarkup:
    """Tone picker shown after a content type, callback gtone:<type>:<tone>."""
    buttons = [
        InlineKeyboardButton(text=i18n.t(f"tone_{key}", lang), callback_data=f"gtone:{content_type}:{key}")
        for key in TONES
    ]
    return InlineKeyboardMarkup(_rows(buttons, per_row=3))


def length_kb(content_type: str, tone: str, lang: str = i18n.DEFAULT_LANG) -> InlineKeyboardMarkup:
    """Length picker, callback glen:<type>:<tone>:<length>."""
    buttons = [
        InlineKeyboardButton(text=i18n.t(f"length_{key}", lang), callback_data=f"glen:{content_type}:{tone}:{key}")
        for key in LENGTHS
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def image_ratio_kb(lang: str = i18n.DEFAULT_LANG) -> InlineKeyboardMarkup:
    """Image aspect picker, callback imgr:<ratio>."""
    buttons = [
        InlineKeyboardButton(text=i18n.t(f"ratio_{key}", lang), callback_data=f"imgr:{key}")
        for key in IMAGE_RATIOS
    ]
    return InlineKeyboardMarkup(_rows(buttons, per_row=3))


def settings_kb(models: dict, current_model: str, current_lang: str, lang: str) -> InlineKeyboardMarkup:
    """Combined settings keyboard: model row + language row."""
    model_buttons = [
        InlineKeyboardButton(
            text=f"{'✅ ' if key == current_model else ''}{key}",
            callback_data=f"setmodel:{key}",
        )
        for key in models
    ]
    lang_buttons = [
        InlineKeyboardButton(
            text=f"{'✅ ' if code == current_lang else ''}{label}",
            callback_data=f"setlang:{code}",
        )
        for code, label in i18n.UI_LANGUAGES.items()
    ]
    return InlineKeyboardMarkup([model_buttons, lang_buttons])


# Keep model_kb as alias for backwards compat in tests
def model_kb(models: dict, current: str) -> InlineKeyboardMarkup:
    """Model picker only (kept for legacy tests). Use settings_kb for new code."""
    buttons = [
        InlineKeyboardButton(
            text=f"{'✅ ' if key == current else ''}{key}",
            callback_data=f"setmodel:{key}",
        )
        for key in models
    ]
    return InlineKeyboardMarkup(_rows(buttons))


def result_kb(lang: str = i18n.DEFAULT_LANG) -> InlineKeyboardMarkup:
    """Actions under a generated result: regenerate + save as template."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(i18n.t("btn_regenerate", lang), callback_data="regen:"),
                InlineKeyboardButton(i18n.t("btn_save_template", lang), callback_data="tplsave"),
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

"""Maps persistent reply-keyboard button taps to their command handlers."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import keyboards as kb
from .. import i18n
from . import actions, admin, basic, library

# Map: action_key -> handler
_ACTION_HANDLERS = {
    "generate": actions.generate_cmd,
    "translate": actions.translate_cmd,
    "summarize": actions.summarize_cmd,
    "image": actions.image_cmd,
    "history": library.history_cmd,
    "templates": library.templates_cmd,
    "help": basic.help_cmd,
    "stats": admin.stats_cmd,
    "top": admin.top_cmd,
}

# Build _DISPATCH mapping label (both langs) -> handler
_DISPATCH = {}
for _action_key, _handler in _ACTION_HANDLERS.items():
    _i18n_key = kb.MENU_BUTTONS[_action_key]
    for _lang in ("en", "uk"):
        _DISPATCH[i18n.t(_i18n_key, _lang)] = _handler

# Exact strings the MessageHandler filter should match.
MENU_LABELS = tuple(_DISPATCH)


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispatch a tapped menu button to its handler."""
    handler = _DISPATCH.get(update.message.text)
    if handler is not None:
        await handler(update, context)

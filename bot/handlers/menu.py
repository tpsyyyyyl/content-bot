"""Maps persistent reply-keyboard button taps to their command handlers."""
from telegram import Update
from telegram.ext import ContextTypes

from .. import keyboards as kb
from . import actions, admin, basic, library

# Button label -> handler that already implements the matching /command.
_DISPATCH = {
    kb.BTN_GENERATE: actions.generate_cmd,
    kb.BTN_TRANSLATE: actions.translate_cmd,
    kb.BTN_SUMMARIZE: actions.summarize_cmd,
    kb.BTN_IMAGE: actions.image_cmd,
    kb.BTN_HISTORY: library.history_cmd,
    kb.BTN_TEMPLATES: library.templates_cmd,
    kb.BTN_HELP: basic.help_cmd,
    kb.BTN_STATS: admin.stats_cmd,
    kb.BTN_TOP: admin.top_cmd,
}

# Exact strings the MessageHandler filter should match.
MENU_LABELS = tuple(_DISPATCH)


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispatch a tapped menu button to its handler."""
    handler = _DISPATCH.get(update.message.text)
    if handler is not None:
        await handler(update, context)

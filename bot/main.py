"""Entry point: wire up all handlers and start polling."""
import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from . import config, db
from .handlers import actions, admin, basic, library, menu, settings


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if not config.TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

    db.init_db()

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", basic.start))
    app.add_handler(CommandHandler("help", basic.help_cmd))
    app.add_handler(CommandHandler("generate", actions.generate_cmd))
    app.add_handler(CommandHandler("translate", actions.translate_cmd))
    app.add_handler(CommandHandler("summarize", actions.summarize_cmd))
    app.add_handler(CommandHandler("image", actions.image_cmd))
    app.add_handler(CommandHandler("history", library.history_cmd))
    app.add_handler(CommandHandler("templates", library.templates_cmd))
    app.add_handler(CommandHandler("settings", settings.settings_cmd))
    app.add_handler(CommandHandler("cancel", actions.cancel_cmd))
    app.add_handler(CommandHandler("stats", admin.stats_cmd))
    app.add_handler(CommandHandler("top", admin.top_cmd))

    # Callbacks (split by regex so each module owns its namespace)
    app.add_handler(CallbackQueryHandler(actions.on_callback, pattern=r"^(gen|tr|gtone|glen|imgr|regen):"))
    app.add_handler(CallbackQueryHandler(library.on_callback, pattern=r"^(tpluse|tplsave)"))
    app.add_handler(CallbackQueryHandler(settings.on_callback, pattern=r"^setmodel:"))
    app.add_handler(CallbackQueryHandler(settings.on_setlang, pattern=r"^setlang:"))

    # Persistent reply-keyboard taps → matching handlers (before the catch-all)
    app.add_handler(MessageHandler(filters.Text(menu.MENU_LABELS), menu.menu_router))

    # Catch-all text router — MUST be last
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, actions.route_text))

    logging.info("Bot starting (polling)…")
    app.run_polling()


if __name__ == "__main__":
    main()

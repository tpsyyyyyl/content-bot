"""Shared handler helper: register/look up the current user."""
from telegram import Update

from .. import db, i18n


def identify(update: Update) -> tuple[int, int]:
    """Return (telegram_id, internal user_id), registering the user if needed."""
    u = update.effective_user
    return u.id, db.get_or_create_user(u.id, u.username)


def user_lang(user_id: int) -> str:
    """Return the user's saved language code, falling back to DEFAULT_LANG."""
    return db.get_lang(user_id) or i18n.DEFAULT_LANG

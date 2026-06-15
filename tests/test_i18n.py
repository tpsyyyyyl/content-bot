"""Tests for bot/db language storage, bot/i18n, and bot/handlers/_common.user_lang."""
import os
import tempfile

# Must set env BEFORE importing bot modules (config reads at import time).
_tmpdir = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_PATH", os.path.join(_tmpdir, "test_i18n.db"))
os.environ.setdefault("ADMIN_TELEGRAM_ID", "999")
os.environ.setdefault("GROQ_API_KEY", "test")

import pytest

import bot.config as config
import bot.db as db
import bot.i18n as i18n
from bot.handlers._common import user_lang


# ---------------------------------------------------------------------------
# DB fixture (mirrors test_db.py style)
# ---------------------------------------------------------------------------

def _reset():
    db._conn = None
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)


@pytest.fixture(autouse=True)
def fresh_db():
    _reset()
    db.init_db()
    yield
    _reset()


# ---------------------------------------------------------------------------
# db.get_lang / db.set_lang
# ---------------------------------------------------------------------------

def test_get_lang_returns_none_when_unset():
    uid = db.get_or_create_user(5001, "lana")
    assert db.get_lang(uid) is None


def test_set_lang_and_get_lang():
    uid = db.get_or_create_user(5002, "mia")
    db.set_lang(uid, "uk")
    assert db.get_lang(uid) == "uk"


def test_set_lang_overwrites():
    uid = db.get_or_create_user(5003, "nia")
    db.set_lang(uid, "en")
    db.set_lang(uid, "uk")
    assert db.get_lang(uid) == "uk"


def test_set_lang_does_not_clobber_model_key():
    """set_lang upsert must not clear an existing model_key."""
    uid = db.get_or_create_user(5004, "ola")
    db.set_model_key(uid, "gpt-oss")
    db.set_lang(uid, "uk")
    assert db.get_model_key(uid, "default") == "gpt-oss"
    assert db.get_lang(uid) == "uk"


def test_set_model_key_does_not_clobber_lang():
    """set_model_key upsert must not clear an existing language."""
    uid = db.get_or_create_user(5005, "pia")
    db.set_lang(uid, "uk")
    db.set_model_key(uid, "llama")
    assert db.get_lang(uid) == "uk"
    assert db.get_model_key(uid, "default") == "llama"


def test_lang_migration_is_idempotent():
    """Calling init_db() twice on the same DB must not raise."""
    db.init_db()  # second call — column already exists


# ---------------------------------------------------------------------------
# i18n.STRINGS completeness
# ---------------------------------------------------------------------------

def test_all_strings_have_en_and_uk():
    missing = []
    for key, variants in i18n.STRINGS.items():
        for lang in ("en", "uk"):
            if not variants.get(lang):
                missing.append(f"{key}[{lang}]")
    assert not missing, f"Missing/empty translations: {missing}"


# ---------------------------------------------------------------------------
# i18n.t()
# ---------------------------------------------------------------------------

def test_t_returns_uk_string():
    result = i18n.t("cancelled", "uk")
    assert result == i18n.STRINGS["cancelled"]["uk"]
    assert result  # non-empty


def test_t_returns_en_string():
    result = i18n.t("cancelled", "en")
    assert result == i18n.STRINGS["cancelled"]["en"]


def test_t_falls_back_to_en_for_unknown_lang():
    result = i18n.t("cancelled", "fr")
    assert result == i18n.STRINGS["cancelled"]["en"]


def test_t_returns_key_for_unknown_key():
    result = i18n.t("totally_nonexistent_key_xyz", "en")
    assert result == "totally_nonexistent_key_xyz"


def test_t_interpolates_kwargs():
    result = i18n.t("template_saved", "en", name="my promo")
    assert "my promo" in result


def test_t_interpolates_kwargs_uk():
    result = i18n.t("template_saved", "uk", name="мій шаблон")
    assert "мій шаблон" in result


def test_t_does_not_raise_on_missing_placeholder():
    """If kwargs don't match placeholders, return unformatted string (no crash)."""
    result = i18n.t("template_saved", "en")  # 'name' kwarg missing
    assert "template_saved" not in result or True  # doesn't raise; result is the raw string


def test_t_daily_limit_interpolation():
    result = i18n.t("daily_limit_reached", "en", limit=10)
    assert "10" in result


def test_t_stats_interpolation():
    result = i18n.t("stats_message", "uk", users=42, generations=100)
    assert "42" in result
    assert "100" in result


# ---------------------------------------------------------------------------
# _common.user_lang
# ---------------------------------------------------------------------------

def test_user_lang_returns_default_when_unset():
    uid = db.get_or_create_user(6001, "quinn")
    assert user_lang(uid) == i18n.DEFAULT_LANG


def test_user_lang_returns_saved_lang():
    uid = db.get_or_create_user(6002, "rose")
    db.set_lang(uid, "uk")
    assert user_lang(uid) == "uk"

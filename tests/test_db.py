"""Tests for bot/db.py — uses a temp SQLite file."""
import os
import tempfile

# Must set env BEFORE importing bot modules (config reads at import time).
_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_PATH"] = os.path.join(_tmpdir, "test.db")
os.environ["ADMIN_TELEGRAM_ID"] = "999"

import importlib
import pytest

import bot.config as config
import bot.db as db


def _reset():
    """Drop module-level connection so each test gets a fresh DB."""
    db._conn = None
    # Remove stale DB file if present.
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)


@pytest.fixture(autouse=True)
def fresh_db():
    _reset()
    db.init_db()
    yield
    _reset()


# ---------------------------------------------------------------------------
# get_or_create_user
# ---------------------------------------------------------------------------

def test_create_user_returns_id():
    uid = db.get_or_create_user(1001, "alice")
    assert isinstance(uid, int) and uid > 0


def test_create_user_idempotent():
    uid1 = db.get_or_create_user(1001, "alice")
    uid2 = db.get_or_create_user(1001, "alice")
    assert uid1 == uid2


# ---------------------------------------------------------------------------
# record_generation + count_today
# ---------------------------------------------------------------------------

def test_record_generation_increments_count_today():
    uid = db.get_or_create_user(1002, "bob")
    assert db.count_today(uid) == 0
    db.record_generation(uid, "social_post", "hello", "world")
    assert db.count_today(uid) == 1
    db.record_generation(uid, "email", "hi", "there")
    assert db.count_today(uid) == 2


def test_record_generation_increments_usage_count():
    uid = db.get_or_create_user(1003, "carol")
    db.record_generation(uid, "social_post", "p", "r")
    rows = db.top_users(limit=10)
    carol = next(r for r in rows if r["username"] == "carol")
    assert carol["usage_count"] == 1


# ---------------------------------------------------------------------------
# remaining_quota
# ---------------------------------------------------------------------------

def test_remaining_quota_decreases():
    uid = db.get_or_create_user(1004, "dave")
    quota_before = db.remaining_quota(1004, uid)
    assert quota_before == config.DAILY_LIMIT
    db.record_generation(uid, "email", "p", "r")
    assert db.remaining_quota(1004, uid) == config.DAILY_LIMIT - 1


def test_remaining_quota_floors_at_zero():
    uid = db.get_or_create_user(1005, "eve")
    for _ in range(config.DAILY_LIMIT + 3):
        db.record_generation(uid, "email", "p", "r")
    assert db.remaining_quota(1005, uid) == 0


def test_remaining_quota_admin_is_none():
    # ADMIN_TELEGRAM_ID is set to 999 in env above.
    uid = db.get_or_create_user(999, "admin")
    result = db.remaining_quota(999, uid)
    assert result is None


# ---------------------------------------------------------------------------
# templates
# ---------------------------------------------------------------------------

def test_save_and_list_templates():
    uid = db.get_or_create_user(2001, "frank")
    db.save_template(uid, "promo", "social_post", "Buy now!")
    db.save_template(uid, "intro", "blog_intro", "Welcome...")
    templates = db.list_templates(uid)
    assert len(templates) == 2
    # newest first
    assert templates[0]["name"] == "intro"


def test_get_template_found():
    uid = db.get_or_create_user(2002, "grace")
    db.save_template(uid, "deal", "ad_copy", "50% off!")
    tmpl = db.get_template(uid, "deal")
    assert tmpl is not None
    assert tmpl["content"] == "50% off!"
    assert tmpl["type"] == "ad_copy"


def test_get_template_not_found():
    uid = db.get_or_create_user(2003, "henry")
    assert db.get_template(uid, "nonexistent") is None


# ---------------------------------------------------------------------------
# stats + top_users
# ---------------------------------------------------------------------------

def test_stats():
    db.get_or_create_user(3001, "ida")
    uid = db.get_or_create_user(3002, "jack")
    db.record_generation(uid, "email", "p", "r")
    s = db.stats()
    assert s["users"] >= 2
    assert s["generations"] >= 1


def test_top_users():
    u1 = db.get_or_create_user(4001, "topA")
    u2 = db.get_or_create_user(4002, "topB")
    for _ in range(3):
        db.record_generation(u1, "email", "p", "r")
    db.record_generation(u2, "email", "p", "r")
    top = db.top_users(limit=2)
    assert top[0]["username"] == "topA"
    assert top[0]["usage_count"] == 3

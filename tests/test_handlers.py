"""Tests for menu routing and the text/callback action handlers."""
from unittest.mock import AsyncMock

import bot.config as config
import bot.db as db
from bot import keyboards as kb
from bot.handlers import actions, menu, settings


# ---------------------------------------------------------------------------
# menu router
# ---------------------------------------------------------------------------

async def test_menu_router_invokes_mapped_handler(monkeypatch, make_update, make_context):
    mock = AsyncMock()
    monkeypatch.setattr(menu, "_DISPATCH", {kb.BTN_GENERATE: mock})
    await menu.menu_router(make_update(text=kb.BTN_GENERATE), make_context())
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# route_text
# ---------------------------------------------------------------------------

async def test_route_text_generate(monkeypatch, make_update, make_context):
    monkeypatch.setattr(actions.ai, "generate", lambda *a, **k: "RESULT")
    ctx = make_context(user_data={"pending": {
        "action": "generate", "content_type": "social_post", "tone": "casual", "length": "short"}})
    upd = make_update(text="brief")
    await actions.route_text(upd, ctx)
    upd.message.reply_text.assert_awaited()
    assert ctx.user_data["last"]["result"] == "RESULT"
    assert ctx.user_data["last"]["kind"] == "social_post"


async def test_route_text_summarize(monkeypatch, make_update, make_context):
    monkeypatch.setattr(actions.ai, "summarize", lambda *a, **k: "SUM")
    ctx = make_context(user_data={"pending": {"action": "summarize"}})
    await actions.route_text(make_update(text="long text"), ctx)
    assert ctx.user_data["last"]["result"] == "SUM"
    assert ctx.user_data["last"]["kind"] == "summarize"


async def test_route_text_image_uses_ratio(monkeypatch, make_update, make_context):
    captured = {}

    def fake_img(prompt, width=1024, height=1024):
        captured["wh"] = (width, height)
        return b"IMG"

    monkeypatch.setattr(actions.image, "generate_image", fake_img)
    ctx = make_context(user_data={"pending": {"action": "image", "ratio": "portrait"}})
    upd = make_update(text="a cat")
    await actions.route_text(upd, ctx)
    upd.message.reply_photo.assert_awaited()
    _, w, h = config.IMAGE_RATIOS["portrait"]
    assert captured["wh"] == (w, h)


async def test_route_text_no_pending(make_update, make_context):
    upd = make_update(text="hi")
    await actions.route_text(upd, make_context())
    assert "Pick a command" in upd.message.reply_text.await_args.args[0]


async def test_route_text_quota_exhausted(monkeypatch, make_update, make_context):
    uid = db.get_or_create_user(1, "tester")  # not admin (admin is 999)
    for _ in range(config.DAILY_LIMIT):
        db.record_generation(uid, "email", "p", "r")
    monkeypatch.setattr(actions.ai, "generate", lambda *a, **k: "SHOULD NOT RUN")
    ctx = make_context(user_data={"pending": {"action": "generate", "content_type": "email"}})
    await actions.route_text(make_update(text="brief", user_id=1), ctx)
    assert "last" not in ctx.user_data


# ---------------------------------------------------------------------------
# cancel
# ---------------------------------------------------------------------------

async def test_cancel_clears_pending(make_update, make_context):
    ctx = make_context(user_data={"pending": {"action": "summarize"}})
    await actions.cancel_cmd(make_update(text="/cancel"), ctx)
    assert "pending" not in ctx.user_data


# ---------------------------------------------------------------------------
# regenerate
# ---------------------------------------------------------------------------

async def test_regenerate_reuses_last(monkeypatch, make_update, make_context):
    monkeypatch.setattr(actions.ai, "generate", lambda *a, **k: "AGAIN")
    last = {
        "action": "generate", "kind": "social_post", "input": "brief", "result": "OLD",
        "content_type": "social_post", "tone": "casual", "length": "short",
    }
    ctx = make_context(user_data={"last": last})
    upd = make_update(callback_data="regen:")
    await actions.on_callback(upd, ctx)
    upd.callback_query.message.reply_text.assert_awaited()
    assert ctx.user_data["last"]["result"] == "AGAIN"


# ---------------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------------

async def test_settings_persists_model(make_update, make_context):
    await settings.on_callback(make_update(callback_data="setmodel:llama"), make_context())
    uid = db.get_or_create_user(1, "tester")
    assert db.get_model_key(uid, "gpt-oss") == "llama"

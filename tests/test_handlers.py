"""Tests for menu routing and the text/callback action handlers."""
from unittest.mock import AsyncMock

import bot.config as config
import bot.db as db
import bot.i18n as i18n
from bot import keyboards as kb
from bot.handlers import actions, basic, menu, settings


# ---------------------------------------------------------------------------
# menu router
# ---------------------------------------------------------------------------

async def test_menu_router_invokes_mapped_handler(monkeypatch, make_update, make_context):
    mock = AsyncMock()
    en_label = i18n.t("btn_generate", "en")
    monkeypatch.setattr(menu, "_DISPATCH", {en_label: mock})
    await menu.menu_router(make_update(text=en_label), make_context())
    mock.assert_awaited_once()


async def test_menu_router_invokes_handler_for_uk_label(monkeypatch, make_update, make_context):
    mock = AsyncMock()
    uk_label = i18n.t("btn_generate", "uk")
    monkeypatch.setattr(menu, "_DISPATCH", {uk_label: mock})
    await menu.menu_router(make_update(text=uk_label), make_context())
    mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------

async def test_start_new_user_shows_language_picker(make_update, make_context):
    """New user (no lang set) should see the choose_language prompt."""
    upd = make_update(user_id=42)
    await basic.start(upd, make_context())
    call_args = upd.message.reply_text.await_args
    text = call_args.args[0]
    assert i18n.t("choose_language", i18n.DEFAULT_LANG) in text
    # keyboard should be the language selector (inline)
    markup = call_args.kwargs.get("reply_markup")
    assert markup is not None


async def test_start_existing_user_shows_welcome(make_update, make_context):
    """User with lang set should see the welcome message in their language."""
    uid = db.get_or_create_user(43, "bob")
    db.set_lang(uid, "uk")
    upd = make_update(user_id=43, first_name="Bob")
    await basic.start(upd, make_context())
    call_args = upd.message.reply_text.await_args
    text = call_args.args[0]
    assert i18n.t("welcome", "uk", name="Bob") == text


# ---------------------------------------------------------------------------
# on_setlang
# ---------------------------------------------------------------------------

async def test_on_setlang_first_time_saves_lang_and_sends_welcome(make_update, make_context):
    """First-time setlang: saves language, edits message, sends welcome."""
    uid = db.get_or_create_user(50, "newuser")
    # No lang set yet — prev is None
    upd = make_update(user_id=50, first_name="Nova", callback_data="setlang:uk")
    # Need a bot mock on context
    ctx = make_context()
    ctx.bot = AsyncMock()
    ctx.bot.send_message = AsyncMock()

    await settings.on_setlang(upd, ctx)

    assert db.get_lang(uid) == "uk"
    upd.callback_query.edit_message_text.assert_awaited_once()
    ctx.bot.send_message.assert_awaited_once()
    # Welcome message should be in Ukrainian
    send_args = ctx.bot.send_message.await_args
    welcome_text = send_args.kwargs.get("text") or send_args.args[1]
    assert i18n.t("welcome", "uk", name="Nova") == welcome_text


async def test_on_setlang_from_settings_rebuilds_screen(make_update, make_context):
    """setlang when prev lang exists: no send_message, just edit_message_text with settings screen."""
    uid = db.get_or_create_user(51, "changer")
    db.set_lang(uid, "en")  # existing lang
    upd = make_update(user_id=51, first_name="Changer", callback_data="setlang:uk")
    ctx = make_context()
    ctx.bot = AsyncMock()
    ctx.bot.send_message = AsyncMock()

    await settings.on_setlang(upd, ctx)

    assert db.get_lang(uid) == "uk"
    upd.callback_query.edit_message_text.assert_awaited_once()
    ctx.bot.send_message.assert_not_awaited()
    # The edited message should contain the settings prompt in uk
    edit_args = upd.callback_query.edit_message_text.await_args
    text = edit_args.args[0] if edit_args.args else edit_args.kwargs.get("text")
    from bot import ai
    current_model = db.get_model_key(uid, ai.DEFAULT_MODEL_KEY)
    assert i18n.t("settings_prompt", "uk", model=current_model) == text


async def test_on_setlang_invalid_code_is_ignored(make_update, make_context):
    uid = db.get_or_create_user(52, "inv")
    upd = make_update(user_id=52, callback_data="setlang:xx")
    ctx = make_context()
    ctx.bot = AsyncMock()
    await settings.on_setlang(upd, ctx)
    assert db.get_lang(uid) is None
    upd.callback_query.edit_message_text.assert_not_awaited()


# ---------------------------------------------------------------------------
# /settings
# ---------------------------------------------------------------------------

async def test_settings_shows_both_model_and_language_pickers(make_update, make_context):
    uid = db.get_or_create_user(60, "settingsuser")
    db.set_lang(uid, "en")
    upd = make_update(user_id=60)
    await settings.settings_cmd(upd, make_context())
    call_args = upd.message.reply_text.await_args
    markup = call_args.kwargs.get("reply_markup") or (call_args.args[1] if len(call_args.args) > 1 else None)
    assert markup is not None
    rows = markup.inline_keyboard
    assert len(rows) == 2  # model row + language row
    lang_datas = {btn.callback_data for btn in rows[1]}
    assert "setlang:uk" in lang_datas
    assert "setlang:en" in lang_datas


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
    text = upd.message.reply_text.await_args.args[0]
    assert i18n.t("no_pending_action", "en") in text


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
# malformed callback data
# ---------------------------------------------------------------------------

async def test_malformed_gtone_callback_does_not_crash(make_update, make_context):
    upd = make_update(callback_data="gtone:onlyone")  # missing the tone segment
    await actions.on_callback(upd, make_context())  # must not raise ValueError
    upd.callback_query.answer.assert_awaited()


# ---------------------------------------------------------------------------
# settings — setmodel
# ---------------------------------------------------------------------------

async def test_settings_persists_model(make_update, make_context):
    upd = make_update(callback_data="setmodel:llama")
    ctx = make_context()
    await settings.on_callback(upd, ctx)
    uid = db.get_or_create_user(1, "tester")
    assert db.get_model_key(uid, "gpt-oss") == "llama"


async def test_settings_setmodel_rebuilds_screen_not_finalizes(make_update, make_context):
    """on_callback (setmodel:) should edit the settings screen, not just say 'Model set'."""
    uid = db.get_or_create_user(1, "tester")
    db.set_lang(uid, "en")
    upd = make_update(callback_data="setmodel:llama")
    await settings.on_callback(upd, make_context())
    edit_args = upd.callback_query.edit_message_text.await_args
    text = edit_args.args[0] if edit_args.args else edit_args.kwargs.get("text")
    # Should show settings_prompt, not the old "Model set to..." message
    assert i18n.t("settings_prompt", "en", model="llama") == text

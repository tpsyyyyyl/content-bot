"""Tests for the persistent main-menu reply keyboard and its router mapping."""
import os

os.environ.setdefault("GROQ_API_KEY", "test")

from bot import i18n
from bot import keyboards as kb
from bot.handlers import menu


def _labels(markup):
    return [btn.text for row in markup.keyboard for btn in row]


def test_main_menu_user_has_no_admin_buttons():
    labels = _labels(kb.main_menu_kb(is_admin=False, lang="en"))
    assert i18n.t("btn_generate", "en") in labels
    assert i18n.t("btn_help", "en") in labels
    assert i18n.t("btn_stats", "en") not in labels
    assert i18n.t("btn_top", "en") not in labels


def test_main_menu_admin_has_stats_and_top():
    labels = _labels(kb.main_menu_kb(is_admin=True, lang="en"))
    assert i18n.t("btn_stats", "en") in labels
    assert i18n.t("btn_top", "en") in labels


def test_keyboard_resizes():
    assert kb.main_menu_kb().resize_keyboard is True


def test_every_menu_label_maps_to_a_handler():
    assert set(menu.MENU_LABELS) == set(menu._DISPATCH)
    assert all(callable(h) for h in menu._DISPATCH.values())


def test_main_menu_uk_labels():
    labels = _labels(kb.main_menu_kb(is_admin=False, lang="uk"))
    assert i18n.t("btn_generate", "uk") in labels
    assert i18n.t("btn_help", "uk") in labels


def test_menu_labels_covers_both_languages():
    """MENU_LABELS should contain labels in both en and uk."""
    for action_key, i18n_key in kb.MENU_BUTTONS.items():
        for lang in ("en", "uk"):
            label = i18n.t(i18n_key, lang)
            assert label in menu.MENU_LABELS, f"Missing label '{label}' (action={action_key}, lang={lang})"


def test_language_select_kb_has_two_buttons():
    kb_result = kb.language_select_kb()
    buttons = [btn for row in kb_result.inline_keyboard for btn in row]
    assert len(buttons) == 2
    datas = {btn.callback_data for btn in buttons}
    assert "setlang:uk" in datas
    assert "setlang:en" in datas


def test_settings_kb_has_model_and_lang_rows():
    from bot import ai
    skb = kb.settings_kb(ai.MODELS, ai.DEFAULT_MODEL_KEY, "en", "en")
    rows = skb.inline_keyboard
    assert len(rows) == 2  # model row + language row
    lang_datas = {btn.callback_data for btn in rows[1]}
    assert "setlang:uk" in lang_datas
    assert "setlang:en" in lang_datas


def test_content_types_kb_uses_i18n():
    ckb = kb.content_types_kb("uk")
    buttons = [btn for row in ckb.inline_keyboard for btn in row]
    labels = {btn.text for btn in buttons}
    assert i18n.t("ct_social_post", "uk") in labels


def test_result_kb_uses_i18n():
    rkb = kb.result_kb("uk")
    buttons = [btn for row in rkb.inline_keyboard for btn in row]
    labels = {btn.text for btn in buttons}
    assert i18n.t("btn_regenerate", "uk") in labels
    assert i18n.t("btn_save_template", "uk") in labels

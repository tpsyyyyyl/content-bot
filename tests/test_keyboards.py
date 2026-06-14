"""Tests for the persistent main-menu reply keyboard and its router mapping."""
import os

os.environ.setdefault("GROQ_API_KEY", "test")

from bot import keyboards as kb
from bot.handlers import menu


def _labels(markup):
    return [btn.text for row in markup.keyboard for btn in row]


def test_main_menu_user_has_no_admin_buttons():
    labels = _labels(kb.main_menu_kb(is_admin=False))
    assert kb.BTN_GENERATE in labels
    assert kb.BTN_HELP in labels
    assert kb.BTN_STATS not in labels
    assert kb.BTN_TOP not in labels


def test_main_menu_admin_has_stats_and_top():
    labels = _labels(kb.main_menu_kb(is_admin=True))
    assert kb.BTN_STATS in labels
    assert kb.BTN_TOP in labels


def test_keyboard_resizes():
    assert kb.main_menu_kb().resize_keyboard is True


def test_every_menu_label_maps_to_a_handler():
    assert set(menu.MENU_LABELS) == set(menu._DISPATCH)
    assert all(callable(h) for h in menu._DISPATCH.values())

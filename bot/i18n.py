"""UI localisation — Ukrainian / English.

Only user-facing strings live here.  AI prompts and LLM instructions stay in
English inside config.py / ai.py and are never translated.
"""

DEFAULT_LANG = "en"

# Displayed on the language-selection screen and in /settings.
UI_LANGUAGES: dict[str, str] = {
    "uk": "🇺🇦 Українська",
    "en": "🇬🇧 English",
}

# ---------------------------------------------------------------------------
# String dictionary
# key -> {"en": "...", "uk": "..."}
# Use {placeholder} for interpolated values.
# ---------------------------------------------------------------------------

STRINGS: dict[str, dict[str, str]] = {

    # ------------------------------------------------------------------
    # Welcome / start
    # ------------------------------------------------------------------
    "welcome": {
        "en": (
            "👋 Hey {name}! I'm your AI content assistant.\n\n"
            "✨ Here's what I can do:\n"
            "  /generate — create social posts, emails, ads, blog intros\n"
            "  /translate — translate text into 6 languages\n"
            "  /summarize — condense long text into key points\n"
            "  /image — generate an image from a description\n"
            "  /history — browse your recent generations\n"
            "  /templates — reuse your saved content\n"
            "  /settings — switch the AI model\n\n"
            "Tap a button below, or /cancel anytime to stop. "
            "Type /help for the full list. Let's create something! 🚀"
        ),
        "uk": (
            "👋 Привіт, {name}! Я твій AI-асистент для створення контенту.\n\n"
            "✨ Що я вмію:\n"
            "  /generate — соціальні пости, листи, рекламні тексти, вступи до блогів\n"
            "  /translate — переклад на 6 мов\n"
            "  /summarize — стислий переказ довгих текстів\n"
            "  /image — генерація зображення за описом\n"
            "  /history — перегляд останніх результатів\n"
            "  /templates — збережені шаблони\n"
            "  /settings — зміна AI-моделі\n\n"
            "Натисни кнопку нижче або /cancel, щоб зупинитись. "
            "Команда /help — повний список. Починаємо! 🚀"
        ),
    },

    # Language selection prompt (bilingual by design — shown before lang is known)
    "choose_language": {
        "en": "🌐 Choose your language / Оберіть мову:",
        "uk": "🌐 Choose your language / Оберіть мову:",
    },

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------
    "help": {
        "en": (
            "📋 *Commands:*\n\n"
            "/generate — pick a content type and get AI-written copy\n"
            "/translate — translate your text into another language\n"
            "/summarize — summarize long text + bullet points\n"
            "/image — generate an image from a text prompt\n"
            "/history — see your last 10 generations\n"
            "/templates — list and reuse saved templates\n"
            "/settings — switch the AI model (gpt-oss / llama)\n"
            "/cancel — stop the current action\n"
            "/stats — admin: user & generation stats\n"
            "/top — admin: top 5 users by usage"
        ),
        "uk": (
            "📋 *Команди:*\n\n"
            "/generate — вибери тип контенту та отримай AI-текст\n"
            "/translate — перекладає твій текст іншою мовою\n"
            "/summarize — стислий переказ + тези\n"
            "/image — генерація зображення за текстом\n"
            "/history — останні 10 генерацій\n"
            "/templates — список і повторне використання шаблонів\n"
            "/settings — зміна AI-моделі (gpt-oss / llama)\n"
            "/cancel — зупинити поточну дію\n"
            "/stats — адмін: статистика користувачів і генерацій\n"
            "/top — адмін: топ-5 користувачів за кількістю запитів"
        ),
    },

    # ------------------------------------------------------------------
    # Generate flow
    # ------------------------------------------------------------------
    "choose_content_type": {
        "en": "Choose a content type:",
        "uk": "Оберіть тип контенту:",
    },
    "choose_tone": {
        "en": "Choose a tone:",
        "uk": "Оберіть тон:",
    },
    "choose_length": {
        "en": "Choose a length:",
        "uk": "Оберіть довжину:",
    },
    "send_brief": {
        "en": "✏️ Now send your brief / topic.",
        "uk": "✏️ Надішліть ваш бриф або тему.",
    },

    # ------------------------------------------------------------------
    # Translate flow
    # ------------------------------------------------------------------
    "choose_target_language": {
        "en": "Choose a target language:",
        "uk": "Оберіть мову перекладу:",
    },
    "send_text_to_translate": {
        "en": "💬 Send the text you want translated.",
        "uk": "💬 Надішліть текст для перекладу.",
    },

    # ------------------------------------------------------------------
    # Summarize flow
    # ------------------------------------------------------------------
    "send_text_to_summarize": {
        "en": "📝 Send the text you want summarized.",
        "uk": "📝 Надішліть текст для стислого переказу.",
    },

    # ------------------------------------------------------------------
    # Image flow
    # ------------------------------------------------------------------
    "choose_image_format": {
        "en": "🎨 Choose an image format:",
        "uk": "🎨 Оберіть формат зображення:",
    },
    "send_image_prompt": {
        "en": "🎨 Send a prompt describing the image.",
        "uk": "🎨 Опишіть зображення, яке хочете створити.",
    },

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    "history_empty": {
        "en": "📭 No history yet.",
        "uk": "📭 Історія порожня.",
    },
    "history_header": {
        "en": "📜 Recent generations:",
        "uk": "📜 Останні генерації:",
    },

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------
    "templates_empty": {
        "en": "📂 No saved templates yet. Generate something, then tap 💾 Save as template.",
        "uk": "📂 Поки що немає збережених шаблонів. Згенеруйте щось і натисніть 💾 Зберегти як шаблон.",
    },
    "templates_header": {
        "en": "📁 Your templates:",
        "uk": "📁 Ваші шаблони:",
    },
    "send_template_name": {
        "en": "📝 Send a name for this template.",
        "uk": "📝 Надішліть назву для цього шаблону.",
    },
    "template_saved": {
        "en": "✅ Saved template '{name}'.",
        "uk": "✅ Шаблон '{name}' збережено.",
    },
    "template_not_found": {
        "en": "⚠️ Template not found.",
        "uk": "⚠️ Шаблон не знайдено.",
    },
    "nothing_to_save": {
        "en": "⚠️ Nothing to save yet.",
        "uk": "⚠️ Ще нічого немає для збереження.",
    },

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    "settings_prompt": {
        "en": "🔧 Current AI model: *{model}*\nPick one:",
        "uk": "🔧 Поточна AI-модель: *{model}*\nОберіть:",
    },
    "model_set": {
        "en": "✅ Model set to *{model}*.",
        "uk": "✅ Модель змінено на *{model}*.",
    },
    "language_set": {
        "en": "✅ Language set to {lang_name}.",
        "uk": "✅ Мову змінено на {lang_name}.",
    },

    # ------------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------------
    "admin_only": {
        "en": "🔒 Admin only.",
        "uk": "🔒 Тільки для адміністратора.",
    },
    "stats_message": {
        "en": "👥 Users: {users}\n✨ Generations: {generations}",
        "uk": "👥 Користувачів: {users}\n✨ Генерацій: {generations}",
    },
    "top_empty": {
        "en": "📊 No usage data yet.",
        "uk": "📊 Даних про використання ще немає.",
    },
    "top_header": {
        "en": "🏆 Top users:",
        "uk": "🏆 Топ користувачів:",
    },

    # ------------------------------------------------------------------
    # Errors / generic responses
    # ------------------------------------------------------------------
    "daily_limit_reached": {
        "en": "⏳ Daily limit reached ({limit}/day). Try again tomorrow.",
        "uk": "⏳ Денний ліміт вичерпано ({limit}/день). Спробуйте завтра.",
    },
    "cancelled": {
        "en": "❌ Cancelled.",
        "uk": "❌ Скасовано.",
    },
    "no_pending_action": {
        "en": "ℹ️ Pick a command first — see /help.",
        "uk": "ℹ️ Спочатку оберіть команду — дивіться /help.",
    },
    "nothing_to_regenerate": {
        "en": "⚠️ Nothing to regenerate yet.",
        "uk": "⚠️ Ще нічого для повторної генерації.",
    },

    # ------------------------------------------------------------------
    # Menu button labels (reply keyboard)
    # ------------------------------------------------------------------
    "btn_generate": {
        "en": "✍️ Generate",
        "uk": "✍️ Генерувати",
    },
    "btn_translate": {
        "en": "🌐 Translate",
        "uk": "🌐 Перекласти",
    },
    "btn_summarize": {
        "en": "📝 Summarize",
        "uk": "📝 Переказати",
    },
    "btn_image": {
        "en": "🎨 Image",
        "uk": "🎨 Зображення",
    },
    "btn_history": {
        "en": "🕘 History",
        "uk": "🕘 Історія",
    },
    "btn_templates": {
        "en": "📋 Templates",
        "uk": "📋 Шаблони",
    },
    "btn_help": {
        "en": "ℹ️ Help",
        "uk": "ℹ️ Довідка",
    },
    "btn_stats": {
        "en": "📊 Stats",
        "uk": "📊 Статистика",
    },
    "btn_top": {
        "en": "🏆 Top",
        "uk": "🏆 Топ",
    },

    # ------------------------------------------------------------------
    # Inline button labels (result keyboard)
    # ------------------------------------------------------------------
    "btn_regenerate": {
        "en": "🔄 Regenerate",
        "uk": "🔄 Згенерувати ще раз",
    },
    "btn_save_template": {
        "en": "💾 Save as template",
        "uk": "💾 Зберегти як шаблон",
    },

    # ------------------------------------------------------------------
    # Content-type labels (user-facing names in the picker)
    # prompt-instruction halves stay in config.py for the LLM
    # ------------------------------------------------------------------
    "ct_social_post": {
        "en": "📱 Social post",
        "uk": "📱 Соцмережі",
    },
    "ct_email": {
        "en": "✉️ Email",
        "uk": "✉️ Email",
    },
    "ct_ad_copy": {
        "en": "📢 Ad copy",
        "uk": "📢 Рекламний текст",
    },
    "ct_blog_intro": {
        "en": "📝 Blog intro",
        "uk": "📝 Вступ до блогу",
    },
    "ct_linkedin_post": {
        "en": "💼 LinkedIn post",
        "uk": "💼 Пост для LinkedIn",
    },
    "ct_product_desc": {
        "en": "🛍️ Product description",
        "uk": "🛍️ Опис товару",
    },

    # ------------------------------------------------------------------
    # Tone labels (generate flow picker)
    # ------------------------------------------------------------------
    "tone_professional": {
        "en": "Professional",
        "uk": "Професійний",
    },
    "tone_casual": {
        "en": "Casual",
        "uk": "Розмовний",
    },
    "tone_funny": {
        "en": "Funny",
        "uk": "Жартівливий",
    },

    # ------------------------------------------------------------------
    # Length labels (generate flow picker)
    # ------------------------------------------------------------------
    "length_short": {
        "en": "Short (~50 words)",
        "uk": "Коротко (~50 слів)",
    },
    "length_long": {
        "en": "Long (~200 words)",
        "uk": "Розгорнуто (~200 слів)",
    },

    # ------------------------------------------------------------------
    # Image ratio labels (image flow picker)
    # ------------------------------------------------------------------
    "ratio_square": {
        "en": "⬜ Square",
        "uk": "⬜ Квадрат",
    },
    "ratio_landscape": {
        "en": "🖼️ Landscape",
        "uk": "🖼️ Горизонтальне",
    },
    "ratio_portrait": {
        "en": "📱 Portrait",
        "uk": "📱 Вертикальне",
    },

    # ------------------------------------------------------------------
    # Target-language labels for /translate picker
    # ------------------------------------------------------------------
    "lang_en": {
        "en": "🇬🇧 English",
        "uk": "🇬🇧 Англійська",
    },
    "lang_uk": {
        "en": "🇺🇦 Ukrainian",
        "uk": "🇺🇦 Українська",
    },
    "lang_ru": {
        "en": "🇷🇺 Russian",
        "uk": "🇷🇺 Російська",
    },
    "lang_de": {
        "en": "🇩🇪 German",
        "uk": "🇩🇪 Німецька",
    },
    "lang_pl": {
        "en": "🇵🇱 Polish",
        "uk": "🇵🇱 Польська",
    },
    "lang_es": {
        "en": "🇪🇸 Spanish",
        "uk": "🇪🇸 Іспанська",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Return the localised string for *key* in *lang*.

    Fallback chain:
      1. STRINGS[key][lang]
      2. STRINGS[key]["en"]   (if lang not present)
      3. key itself           (if key not in STRINGS)
    Then .format(**kwargs) is applied; if formatting fails the unformatted
    string is returned so the bot never crashes on a missing placeholder.
    """
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text

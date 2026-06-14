# HANDOFF — AI Content Assistant Bot (Фаза 2, Проєкт 3)

**Стан на 2026-06-14:** код повністю готовий і закомічений, тести зелені. Залишився
ТІЛЬКИ smoke-тест наживо + деплой на Fly + push на GitHub — заблоковано бо немає
креденшалів (див. нижче).

## Що це
Telegram-бот: генерація контенту / переклад / підсумовування / генерація зображень.
Polling, python-telegram-bot 22.7, Groq (`openai/gpt-oss-120b`), Pollinations.ai
(free image gen), SQLite. Деплой задуманий як **Fly.io worker** (без HTTP-порту).

Свідомі відхилення від Obsidian-плану (узгоджено з користувачем): Groq замість Claude API;
Pollinations замість DALL-E; Fly.io замість Railway. Обсяг — повний.

## Структура
```
bot/
  config.py     env + константи (CONTENT_TYPES, LANGUAGES, DAILY_LIMIT=10, HISTORY_LIMIT=50)
  ai.py         Groq lazy-singleton; generate/translate/summarize; реєстр MODELS (gpt-oss/llama)
  db.py         stdlib sqlite3; users/history/templates; remaining_quota (admin=unlimited)
  image.py      Pollinations: generate_image(prompt) -> bytes
  keyboards.py  inline-клавіатури
  handlers/
    basic.py      /start /help
    actions.py    /generate /translate /summarize /image + on_callback(gen:/tr:) + route_text (єдиний текст-роутер)
    library.py    /history /templates + on_callback(tpluse:/tplsave)
    admin.py      /stats /top (тільки ADMIN_TELEGRAM_ID)
  main.py       реєстрація хендлерів + run_polling()
tests/          18 тестів (test_db / test_ai / test_image), мок Groq+httpx
Dockerfile, .dockerignore, fly.toml, README.md, .env.example
```

### Архітектурний патерн (важливо)
- Транзитний стан розмови — у `context.user_data["pending"]` (dict з `action`).
- Один `MessageHandler(TEXT & ~COMMAND)` = `actions.route_text` дістає `pending` і диспетчеризує.
- Callback-схема: `gen:<type>`, `tr:<lang>`, `tpluse:<id>`, `tplsave`. Два CallbackQueryHandler
  розділені regex-патернами (actions vs library).
- Після генерації `context.user_data["last"]` тримає результат для кнопки «💾 Save as template».

## Команди запуску
```bash
cd /home/bohdan/study/content-bot
.venv/bin/python -m pytest tests/ -q          # 18 passed
# локальний запуск (потрібен .env з токенами):
.venv/bin/python -m bot.main
```
venv: `/home/bohdan/study/content-bot/.venv` (Python 3.14, PTB 22.7 ставиться чисто).

## ⛔ ЧИМ ЗАБЛОКОВАНО — потрібні креденшали (текстом, не скріншотом)
Перевірка `printenv` показала: **жоден з них НЕ заданий глобально** станом на 14.06,
хоча користувач вважав, що `GROQ_API_KEY` має бути глобальним. Тобто наступний крок —
або виставити їх глобально (`~/.zshrc`/`~/.zshenv`), або створити локальний `.env`:
1. `TELEGRAM_BOT_TOKEN` — з @BotFather (`/newbot`), формат `123456789:AAH...`
2. `ADMIN_TELEGRAM_ID` — числовий id з @userinfobot
3. `GROQ_API_KEY` — той самий ключ, що в price-monitor/landing-studio (`gsk_...`)

## Наступні кроки (Task #7)
1. Створити `.env` (cp `.env.example` → `.env`, заповнити 3 значення).
2. Smoke-тест локально: `python -m bot.main`, у Telegram пройти /start, /generate (всі типи),
   /translate, /summarize, /image (має прийти картинка), /history, /templates,
   /stats+/top (лише з admin id); перевірити rate-limit на 11-му запиті.
3. Деплой: `~/.fly/bin/fly launch` (без деплою) → `fly volumes create content_data --region fra`
   → `fly secrets set TELEGRAM_BOT_TOKEN=... GROQ_API_KEY=... ADMIN_TELEGRAM_ID=...`
   → `fly deploy --ha=false`. Після деплою `fly scale count 1` (polling має жити завжди,
   бо в fly.toml нема service-scoped auto_start/stop ключів — вони валідні тільки в [http_service]).
4. GitHub: створити `tpsyyyyyl/content-bot` (`gh repo create`), push. У батьк. репо `study/`
   вже додано `content-bot/` у `.gitignore`.
5. README: додати demo-GIF та `@ім'я_бота` (плейсхолдери вже стоять).

## Коміти
- `8b9e016` feat: вся кодова база бота.

# 🤖 AI Content Assistant Bot

A multi-purpose AI Telegram bot for content generation, translation, summarization, and image generation — powered by Groq and Pollinations.ai.

---

## ✨ Features

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and quick intro |
| `/help` | Full command reference |
| `/generate` | Generate content — social post, email, ad copy, or blog intro |
| `/translate` | Translate text into EN / UK / RU / DE / PL / ES |
| `/summarize` | Summarize any text or pasted article |
| `/image` | Generate an image via Pollinations.ai (free, no API key needed) |
| `/history` | View your last 10 requests |
| `/templates` | Browse and apply pre-built prompt templates |
| `/stats` | *(Admin)* Usage statistics across all users |
| `/top` | *(Admin)* Top users by request count |

Free tier: **10 AI requests per day** per user. Resets at midnight UTC.

---

## 🛠 Tech Stack

- **Python 3.12**
- **python-telegram-bot 22.7** — async, long-polling (no webhook required)
- **Groq** (`openai/gpt-oss-120b`) — fast LLM inference for text tasks
- **Pollinations.ai** — free, open image generation (no API key)
- **SQLite** — lightweight persistent storage for history and rate-limiting
- **Fly.io** — deployed as a persistent worker (no HTTP port)

---

## 🚀 Local Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/tpsyyyyyl/content-bot.git
cd content-bot

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and fill in the values (see below)

# 5. Run
python -m bot.main
```

### Environment variables (`.env`)

| Variable | How to get it |
|----------|---------------|
| `TELEGRAM_BOT_TOKEN` | Create a bot via [@BotFather](https://t.me/BotFather) |
| `GROQ_API_KEY` | Sign up at [console.groq.com](https://console.groq.com) |
| `ADMIN_TELEGRAM_ID` | Send a message to [@userinfobot](https://t.me/userinfobot) |

---

## 🧪 Tests

```bash
pytest tests/ -q
```

---

## ☁️ Deploy on Fly.io

```bash
# First deploy — creates the app and volume
fly launch --no-deploy
fly volumes create content_data --region fra --size 1
fly deploy --ha=false

# Set secrets (bot won't start without these)
fly secrets set \
  TELEGRAM_BOT_TOKEN=your_token \
  GROQ_API_KEY=your_key \
  ADMIN_TELEGRAM_ID=your_telegram_id

# Check it's running
fly logs
fly status
```

The bot runs as a **polling worker** — no HTTP port is exposed. The Fly machine is kept alive permanently via the persistent volume and `min_machines_running = 1` (set this in the Fly dashboard or via `fly scale count 1` after deploy).

---

## 📁 Project Structure

```
content-bot/
├── bot/
│   ├── main.py          # Entry point — starts polling
│   ├── handlers/        # Command and message handlers
│   ├── services/        # Groq client, image generation
│   └── database/        # SQLite models and queries
├── tests/
├── requirements.txt
├── Dockerfile
├── fly.toml
└── .env.example
```

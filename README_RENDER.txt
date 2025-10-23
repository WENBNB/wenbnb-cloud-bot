============================================================
  WENBNB Neural Engine v5.5 — Render Deployment Notes
============================================================

📦 Build Command:
    pip install -r requirements.txt

🚀 Start Command:
    python wenbot.py

🌐 Health Check:
    https://<your-service>.onrender.com/ping

🧠 Required Environment Variables:
------------------------------------------------------------
TELEGRAM_TOKEN       = Your Telegram Bot Token
OPENAI_API_KEY       = Your OpenAI API Key
DASHBOARD_URL        = https://wenbnb-dashboard.onrender.com
DASHBOARD_KEY        = (optional secret key if dashboard protected)
ADMIN_CHAT_ID        = Your Telegram User ID
BSCSCAN_KEY          = Your BscScan API Key (optional)
PORT                 = 10000
------------------------------------------------------------

🧩 Features Enabled in v5.5:
------------------------------------------------------------
🤖 /price           - Live price tracking (Binance + CoinGecko)
💰 /tokeninfo       - Contract analytics via BscScan
🎁 /airdropcheck    - Wallet eligibility checker
😂 /meme            - AI-powered meme generator
📈 /aianalyze       - Neural market insight (AI Core)
🧬 /memory          - Emotion Context Mode v4.1 (AI Soul Integration)
🎮 /giveaway_start  - Admin-only event start
🔒 /giveaway_end    - Admin-only event close
⚙️ /system          - Resource + uptime monitor
💬 Auto-Reply       - Natural conversation AI
🌐 Dashboard Sync   - Live logging via /update_activity
------------------------------------------------------------

🧠 Power Tag:
------------------------------------------------------------
🚀 Powered by WENBNB Neural Engine v5.5
AI + Web3 Core Intelligence 24×7
------------------------------------------------------------

🪄 Developer Notes:
- Default port: 10000 (Render auto-assigns)
- Flask `/ping` keeps Render instance alive
- Update Dashboard URL in `.env` for correct sync
- Full plugin modularity (each feature in /plugins folder)
- Optional R2/S3 integration via `r2_sync.py`

📍 GitHub Repo:
   https://github.com/<your-username>/wenbnb-neural-engine
============================================================

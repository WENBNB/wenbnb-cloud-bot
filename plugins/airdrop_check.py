from telegram.ext import CommandHandler
from telegram import Update
import requests, os, html

# === Branding ===
BRAND_FOOTER = "🎁 Powered by <b>WENBNB Neural Engine</b> — Airdrop Intelligence 24×7 ⚡"
BSCSCAN_BASE = "https://api.bscscan.com/api"

# === Core Function ===
def check_airdrop_status(contract_address):
    """Fetch token airdrop or holder summary from BscScan"""
    api_key = os.getenv("BSCSCAN_API_KEY")
    if not api_key:
        return "⚠️ BscScan API key not configured."

    try:
        url = (
            f"{BSCSCAN_BASE}?module=token&action=tokenholderlist"
            f"&contractaddress={contract_address}&apikey={api_key}"
        )
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("status") == "1":
            holders = len(data.get("result", []))
            return f"✅ Airdrop active — <b>{holders}</b> unique holders detected."
        else:
            msg = data.get("message", "Unknown error")
            return f"⚠️ Could not fetch airdrop data ({html.escape(msg)})."
    except Exception as e:
        return f"⚙️ Neural Engine sync issue: {e}"

# === /airdropcheck Command ===
def airdropcheck_cmd(update: Update, context):
    chat_id = update.effective_chat.id
    args = context.args
    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # 🧠 Fallback to default token if none given
    token_address = ""
    if args:
        token_address = args[0].strip()
    else:
        token_address = os.getenv("WEN_TOKEN_ADDRESS")

    if not token_address:
        update.message.reply_text(
            "💡 Usage: /airdropcheck <contract_address>\n\n"
            "Or set your token in environment variable <code>WEN_TOKEN_ADDRESS</code>.",
            parse_mode="HTML"
        )
        return

    result = check_airdrop_status(token_address)

    # 🧩 AI-style adaptive message
    if "active" in result.lower():
        emoji = "🎉"
        mood = "That’s exciting news — the airdrop seems to be live and distributing!"
    elif "holders" in result.lower():
        emoji = "✨"
        mood = "Strong holder activity detected — nice traction!"
    else:
        emoji = "🕵️"
        mood = "No active distribution found. Keep an eye out for announcements."

    msg = (
        f"{emoji} <b>Airdrop Status</b>\n\n"
        f"{result}\n\n"
        f"🧠 {mood}\n\n"
        f"{BRAND_FOOTER}"
    )

    update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdropcheck_cmd))
    print("✅ Loaded plugin: plugins.airdrop_check (v8.0.6-Stable+)")

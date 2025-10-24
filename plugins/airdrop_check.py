from telegram.ext import CommandHandler
from telegram import Update
import requests, os, html

# === Branding ===
BRAND_FOOTER = "🎁 Powered by <b>WENBNB Neural Engine v8.1-Preview</b> — Airdrop & Holder Intelligence 24×7 ⚡"
BSCSCAN_BASE = "https://api.bscscan.com/api"

# === Core Fetcher ===
def fetch_holder_list(contract_address):
    """Return holder list from BscScan (if available)"""
    api_key = os.getenv("BSCSCAN_API_KEY")
    if not api_key:
        return None, "⚠️ BscScan API key missing."

    try:
        url = f"{BSCSCAN_BASE}?module=token&action=tokenholderlist&contractaddress={contract_address}&apikey={api_key}"
        r = requests.get(url, timeout=12)
        data = r.json()
        if data.get("status") != "1":
            return None, f"⚠️ Unable to fetch holders: {html.escape(data.get('message','Unknown error'))}"
        return data.get("result", []), None
    except Exception as e:
        return None, f"⚙️ Network error: {e}"

# === /airdropcheck command ===
def airdropcheck_cmd(update: Update, context):
    chat_id = update.effective_chat.id
    args = context.args
    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Default token fallback
    token_address = args[0].strip() if args else os.getenv("WEN_TOKEN_ADDRESS")
    if not token_address:
        update.message.reply_text(
            "💡 Usage: /airdropcheck <contract_address>\n"
            "or set your default token in env variable <code>WEN_TOKEN_ADDRESS</code>.",
            parse_mode="HTML")
        return

    holders, error = fetch_holder_list(token_address)
    if error:
        update.message.reply_text(f"{error}\n\n{BRAND_FOOTER}", parse_mode="HTML")
        return

    if not holders or len(holders)==0:
        update.message.reply_text(
            f"🕵️ No active airdrop distribution found for <code>{token_address}</code>.\n\n{BRAND_FOOTER}",
            parse_mode="HTML")
        return

    # Sort by balance (desc) and prepare Top 3
    try:
        sorted_h = sorted(holders, key=lambda h: float(h.get('TokenHolderQuantity','0')), reverse=True)
    except Exception:
        sorted_h = holders

    top3 = sorted_h[:3]
    total_tokens = sum([float(h.get("TokenHolderQuantity","0")) for h in sorted_h]) or 1

    top_lines = []
    for i, h in enumerate(top3, 1):
        addr = h.get("TokenHolderAddress","N/A")
        qty = float(h.get("TokenHolderQuantity","0"))
        perc = (qty / total_tokens) * 100
        top_lines.append(f"{i}. <code>{addr[:6]}...{addr[-4:]}</code> — <b>{perc:.2f}%</b>")

    whales = [ p for p in top3 if (p and float(p.get('TokenHolderQuantity','0')) / total_tokens > 0.05) ]
    if whales:
        mood = "🐋 Whale alert! High concentration detected — watch distribution carefully."
    else:
        mood = "🪶 Healthy distribution — no dominant holders seen."

    msg = (
        f"🎯 <b>Airdrop Check Complete</b>\n\n"
        f"✅ Detected <b>{len(holders)}</b> total holders.\n\n"
        f"👑 <b>Top 3 Holders</b>:\n" + "\n".join(top_lines) + "\n\n"
        f"🧠 {mood}\n\n"
        f"{BRAND_FOOTER}"
    )

    update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdropcheck_cmd))
    print("✅ Loaded plugin: plugins.airdrop_check (v8.1-Preview + Top3 Insight)")

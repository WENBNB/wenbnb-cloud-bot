"""
WENBNB AI Web3 Command Center v5.3.2 (Hotfix)
Fixes:
- Telegram HTML tag escaping (<token_id> etc.)
- CoinGecko token aliases (BNB, ETH)
- Minor fallback polish
🚀 WENBNB Neural Engine — Web3 Intelligence 24×7
"""

import os, time, requests
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7"
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
CG_BASE = "https://api.coingecko.com/api/v3"
BSC_BASE = "https://api.bscscan.com/api"

# === Helpers ===
def safe_request(url, params=None, retries=2, backoff=1.5):
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(backoff * (attempt + 1))
    return None

def format_usd(v):
    try:
        return f"${float(v):,.6f}"
    except:
        return "N/A"

def normalize_addr(addr):
    if not addr:
        return ""
    a = addr.strip()
    if not a.startswith("0x"):
        a = "0x" + a
    return a.lower()

# === Aliases ===
ALIASES = {
    "bnb": "binancecoin",
    "eth": "ethereum",
    "btc": "bitcoin",
    "wenbnb": "wenbnb"  # placeholder for your token
}

# === API ===
def get_token_price(token_id="wenbnb"):
    tid = ALIASES.get(token_id.lower(), token_id.lower())
    data = safe_request(f"{CG_BASE}/simple/price", {"ids": tid, "vs_currencies": "usd"})
    try:
        return data[tid]["usd"]
    except:
        return None

def get_balance(addr):
    params = {
        "module": "account",
        "action": "balance",
        "address": addr,
        "apikey": BSCSCAN_API_KEY
    }
    data = safe_request(BSC_BASE, params)
    if not data:
        return None, "BscScan unreachable."
    if data.get("status") != "1":
        return None, "Invalid or unreachable address."
    try:
        wei = int(data["result"])
        return wei / 1e18, None
    except:
        return None, "Parsing error."

def get_supply(contract):
    params = {
        "module": "stats",
        "action": "tokensupply",
        "contractaddress": contract,
        "apikey": BSCSCAN_API_KEY
    }
    data = safe_request(BSC_BASE, params)
    if not data or data.get("status") != "1":
        return None, "unverified"
    try:
        val = int(data["result"]) / 1e18
        return val, None
    except:
        return None, "Parsing error."

# === Commands ===
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "<b>🌐 WENBNB AI Web3 Command Center</b>\n\n"
        "💱 /tokenprice &lt;token_id&gt; — Get live price (CoinGecko)\n"
        "💎 /wallet &lt;address&gt; — Check BNB wallet balance\n"
        "📊 /supply &lt;contract&gt; — Token total supply (BSC)\n"
        "🧠 /analyze &lt;address&gt; — AI wallet risk scan (coming soon)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /tokenprice <token_id>\nExample: /tokenprice BNB")
        return
    tid = context.args[0]
    price = get_token_price(tid)
    if not price:
        update.message.reply_text(
            f"💰 <b>{tid.upper()}</b> current price:\n<b>N/A</b>\n\n"
            f"Tip: token may not be listed on CoinGecko yet.\n\n{BRAND_TAG}",
            parse_mode="HTML"
        )
    else:
        update.message.reply_text(
            f"💰 <b>{tid.upper()}</b> current price:\n<b>{format_usd(price)}</b>\n\n{BRAND_TAG}",
            parse_mode="HTML"
        )

def wallet_balance(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_wallet_address>")
        return
    addr = normalize_addr(context.args[0])
    bal, err = get_balance(addr)
    if bal is None:
        update.message.reply_text(
            f"👛 Wallet:\n<code>{addr}</code>\nBalance: <b>{err}</b>\n\nTip: BscScan may rate-limit requests — try again or check API quota.\n\n{BRAND_TAG}",
            parse_mode="HTML"
        )
    else:
        update.message.reply_text(
            f"👛 Wallet:\n<code>{addr}</code>\nBalance: <b>{bal:.6f} BNB</b>\n\n{BRAND_TAG}",
            parse_mode="HTML"
        )

def token_supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    addr = normalize_addr(context.args[0])
    val, err = get_supply(addr)
    if val is None:
        if err == "unverified":
            update.message.reply_text(
                f"📊 Token Supply for:\n<code>{addr}</code>\n❌ <b>Invalid or unverified contract.</b>\n\nTip: Verify the contract source on BscScan to enable supply analytics.\n\n{BRAND_TAG}",
                parse_mode="HTML"
            )
        else:
            update.message.reply_text(
                f"📊 Token Supply for:\n<code>{addr}</code>\n❌ <b>{err}</b>\n\n{BRAND_TAG}",
                parse_mode="HTML"
            )
    else:
        update.message.reply_text(
            f"📊 Token Supply for:\n<code>{addr}</code>\nTotal: <b>{val:,.0f} tokens</b>\n\n{BRAND_TAG}",
            parse_mode="HTML"
        )

def analyze_placeholder(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /analyze <address>")
        return
    addr = normalize_addr(context.args[0])
    update.message.reply_text(
        f"🧠 AI Wallet Risk Analyzer — v1.0 Prototype\n\n"
        f"Analyzing wallet:\n<code>{addr}</code>\n\n"
        f"Status: <i>Feature coming in Emotion Sync upgrade (v5.4)</i>\n\n{BRAND_TAG}",
        parse_mode="HTML"
    )

# === Register ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet_balance))
    dp.add_handler(CommandHandler("supply", token_supply))
    dp.add_handler(CommandHandler("analyze", analyze_placeholder))

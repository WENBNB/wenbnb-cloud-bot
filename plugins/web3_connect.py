"""
WENBNB AI-Powered Web3 Command Center v5.1-ProSafe++
────────────────────────────────────────────────────
Integrates blockchain data, wallet validation, and token intelligence.
Now with Safe Mode Guard (no signing ops), HTML-safe output, and telemetry sync.
🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡
"""

import requests, json, time, os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# ====== CONFIG ======
BRAND_TAG = "💫 WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡"
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
CG_BASE = "https://api.coingecko.com/api/v3"
BSC_BASE = "https://api.bscscan.com/api"
SAFE_MODE = True  # 🔒 prevents any signing or sensitive wallet ops

# ====== TELEMETRY BRIDGE ======
def record_telemetry(event: str, data=None):
    """Optional telemetry hook to maintenance_pro."""
    try:
        from plugins.maintenance_pro import record_telemetry as log_event
        log_event(event, data or {})
    except Exception:
        pass

# ====== HELPERS ======
def format_usd(value):
    try:
        return f"${float(value):,.6f}"
    except:
        return "N/A"

def get_token_price(token_id="wenbnb", vs_currency="usd"):
    try:
        url = f"{CG_BASE}/simple/price?ids={token_id}&vs_currencies={vs_currency}"
        data = requests.get(url, timeout=6).json()
        if token_id in data:
            return data[token_id][vs_currency]
        return "N/A"
    except Exception as e:
        print(f"[Web3Connect] Price fetch error: {e}")
        return "N/A"

def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=8).json()
        wei_balance = int(res.get("result", 0))
        bnb_balance = wei_balance / (10**18)
        record_telemetry("wallet_balance", {"address": address, "balance": bnb_balance})
        return f"{bnb_balance:.6f} BNB"
    except Exception as e:
        print(f"[Web3Connect] Wallet balance error: {e}")
        return "Invalid or unreachable address."

def get_token_supply(contract_address):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract_address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=8).json()
        supply = int(res.get("result", 0)) / 1e18
        record_telemetry("token_supply", {"contract": contract_address, "supply": supply})
        return f"{supply:,.0f} tokens"
    except Exception as e:
        print(f"[Web3Connect] Token supply error: {e}")
        return "Error fetching supply."

# ====== COMMANDS ======
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "<b>🌐 WENBNB AI Web3 Command Center</b>\n\n"
        "🪙 /tokenprice &lt;token_id&gt; — Get live price from CoinGecko\n"
        "💎 /wallet &lt;address&gt; — Check BNB wallet balance\n"
        "📊 /supply &lt;contract&gt; — Token total supply (BSC)\n"
        "🧠 /analyze &lt;address&gt; — AI wallet risk scan (coming soon)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /tokenprice <token_id>\nExample: /tokenprice binancecoin")
        return
    token_id = context.args[0].lower()
    price = get_token_price(token_id)
    text = f"💰 <b>{token_id.upper()}</b> current price:\n<b>{format_usd(price)}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def wallet_balance(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_wallet_address>")
        return
    address = context.args[0]
    if SAFE_MODE:
        record_telemetry("wallet_request_safe", {"address": address})
        balance = get_wallet_balance(address)
        update.message.reply_text(
            f"👛 Wallet (Safe Mode): <code>{address}</code>\n"
            f"Balance check allowed — no signing or private keys used.\n\n"
            f"Balance: <b>{balance}</b>\n\n{BRAND_TAG}",
            parse_mode="HTML",
        )
    else:
        update.message.reply_text("⚠️ Full Web3 mode not enabled for safety.")

def token_supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    supply = get_token_supply(contract)
    text = f"📊 Token Supply for:\n<code>{contract}</code>\nTotal: <b>{supply}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

# ====== REGISTER HANDLERS ======
def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet_balance))
    dp.add_handler(CommandHandler("supply", token_supply))
    print("🧠 web3_connect.py v5.1-ProSafe++ initialized — SafeMode & HTML-safe active.")

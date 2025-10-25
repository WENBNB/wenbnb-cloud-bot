"""
WENBNB AI-Powered Web3 Command Center v5.2-ProHybrid ⚡
────────────────────────────────────────────────────────
Now with:
• Auto CoinGecko ID fallback (BNB → binancecoin)
• DexScreener price backup
• Safe Mode + HTML-safe output + telemetry
"""

import requests, json, os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
BRAND_TAG = "💫 WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡"
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
CG_BASE = "https://api.coingecko.com/api/v3"
BSC_BASE = "https://api.bscscan.com/api"
SAFE_MODE = True

# === TELEMETRY SYNC ===
def record_telemetry(event: str, data=None):
    try:
        from plugins.maintenance_pro import record_telemetry as log_event
        log_event(event, data or {})
    except Exception:
        pass

# === HELPERS ===
def format_usd(value):
    try:
        return f"${float(value):,.6f}"
    except:
        return "N/A"

def resolve_token_id(name: str) -> str:
    """Map common aliases to CoinGecko IDs."""
    aliases = {
        "bnb": "binancecoin",
        "wbnb": "wbnb",
        "wenbnb": "wenbnb",
        "busd": "binance-usd",
        "eth": "ethereum",
        "btc": "bitcoin",
    }
    return aliases.get(name.lower(), name.lower())

def get_token_price(token_id="wenbnb", vs_currency="usd"):
    try:
        resolved_id = resolve_token_id(token_id)
        url = f"{CG_BASE}/simple/price?ids={resolved_id}&vs_currencies={vs_currency}"
        res = requests.get(url, timeout=6).json()
        if resolved_id in res:
            price = res[resolved_id][vs_currency]
            record_telemetry("token_price", {"id": token_id, "price": price})
            return price
        # === fallback to DexScreener ===
        dex_url = f"https://api.dexscreener.com/latest/dex/search?q={token_id}"
        dex_data = requests.get(dex_url, timeout=6).json()
        if "pairs" in dex_data and dex_data["pairs"]:
            price_usd = dex_data["pairs"][0].get("priceUsd")
            if price_usd:
                record_telemetry("token_price_dex", {"id": token_id, "price": price_usd})
                return float(price_usd)
        return "N/A"
    except Exception as e:
        print(f"[Web3Connect] Token price error: {e}")
        return "N/A"

def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=8).json()
        wei_balance = int(res.get("result", 0))
        bnb_balance = wei_balance / (10**18)
        record_telemetry("wallet_balance", {"address": address, "balance": bnb_balance})
        return f"{bnb_balance:.6f} BNB"
    except:
        return "Invalid or unreachable address."

def get_token_supply(contract_address):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract_address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=8).json()
        supply = int(res.get("result", 0)) / 1e18
        record_telemetry("token_supply", {"contract": contract_address, "supply": supply})
        return f"{supply:,.0f} tokens"
    except:
        return "Error fetching supply."

# === COMMANDS ===
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "<b>🌐 WENBNB AI Web3 Command Center</b>\n\n"
        "🪙 /tokenprice &lt;token_id&gt; — Get live price (CoinGecko + DexScreener)\n"
        "💎 /wallet &lt;address&gt; — Check BNB wallet balance\n"
        "📊 /supply &lt;contract&gt; — Token total supply (BSC)\n"
        "🧠 /analyze &lt;address&gt; — AI wallet risk scan (coming soon)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /tokenprice <token_id>\nExample: /tokenprice bnb")
        return
    token_id = context.args[0]
    price = get_token_price(token_id)
    text = f"💰 <b>{token_id.upper()}</b> current price:\n<b>{format_usd(price)}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def wallet_balance(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_wallet_address>")
        return
    address = context.args[0]
    balance = get_wallet_balance(address)
    if SAFE_MODE:
        update.message.reply_text(
            f"👛 Wallet (Safe Mode): <code>{address}</code>\n"
            f"Balance: <b>{balance}</b>\n\n"
            f"Balance check allowed — no private keys used.\n\n{BRAND_TAG}",
            parse_mode="HTML",
        )
    else:
        update.message.reply_text(f"Balance: {balance}\n\n{BRAND_TAG}", parse_mode="HTML")

def token_supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    supply = get_token_supply(contract)
    text = f"📊 Token Supply for:\n<code>{contract}</code>\nTotal: <b>{supply}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

# === REGISTER HANDLERS ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet_balance))
    dp.add_handler(CommandHandler("supply", token_supply))
    print("🧠 web3_connect.py v5.2-ProHybrid loaded — Dex fallback & Safe Mode active.")

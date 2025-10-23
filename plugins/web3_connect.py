"""
WENBNB AI-Powered Web3 Command Center v4.5 (Hybrid)
Integrates blockchain data, wallet validation, and token intelligence.
Locked & Approved — Full Neural Integration.
"""

import requests, json, time, os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# ====== CONFIGURATION ======
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
CG_BASE = "https://api.coingecko.com/api/v3"
BSC_BASE = "https://api.bscscan.com/api"

# ====== HELPERS ======

def format_usd(value):
    try:
        return f"${float(value):,.6f}"
    except:
        return "N/A"

def get_token_price(token_id="wenbnb", vs_currency="usd"):
    try:
        url = f"{CG_BASE}/simple/price?ids={token_id}&vs_currencies={vs_currency}"
        data = requests.get(url).json()
        return data[token_id][vs_currency]
    except:
        return "N/A"

def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        wei_balance = int(res.get("result", 0))
        bnb_balance = wei_balance / (10**18)
        return f"{bnb_balance:.6f} BNB"
    except:
        return "Invalid or unreachable address."

def get_token_supply(contract_address):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract_address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        return f"{int(res.get('result', 0)) / 1e18:,.0f} tokens"
    except:
        return "Error fetching supply."

# ====== COMMANDS ======

def web3_panel(update: Update, context: CallbackContext):
    text = (
        "<b>🌐 WENBNB AI Web3 Command Center</b>\n\n"
        "🪙 /tokenprice <id> — Get live price from CoinGecko\n"
        "💎 /wallet <address> — Check BNB wallet balance\n"
        "📊 /supply <contract> — Token total supply (BSC)\n"
        "🧠 /analyze <address> — AI risk scan for wallet (coming soon)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /tokenprice <token_id>\nExample: /tokenprice wenbnb")
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
    balance = get_wallet_balance(address)
    text = f"👛 Wallet: <code>{address}</code>\nBalance: <b>{balance}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

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

"""
WENBNB Web3 Connect v5.8.2-ProPulse+ UIx
────────────────────────────────────────────
Visual overhaul + data reliability fix
💫 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡
"""

import requests, os, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡"

# === CORE LINKS ===
BSC_BASE = "https://api.bscscan.com/api"
DEX_URL = "https://api.dexscreener.com/latest/dex/tokens/{contract}"
CG_URL = "https://api.coingecko.com/api/v3/simple/price?ids={tid}&vs_currencies=usd"

ALIASES = {
    "bnb": ("binancecoin", "0xb8c77482e45f1f44de1745f52c74426c631bdd52"),
    "eth": ("ethereum", "0x2170ed0880ac9a755fd29b2688956bd959f933f8"),
    "btc": ("bitcoin", "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c"),
    "doge": ("dogecoin", "0xba2ae424d960c26247dd6c32edc70b295c744c43"),
    "floki": ("floki", "0xfb5b838b6cfeedc2873ab27866079ac55363d37e"),
    "tokenfi": ("tokenfi", "0x4507cef57c46789ef8d1a19ea45f4216bae2b528"),
    "wenbnb": ("wenbnb", "0x4507cef57c46789ef8d1a19ea45f4216bae2b528"),
}

# === TOKEN PRICE ENGINE ===
def get_token_price(token: str):
    token = token.lower()
    if token not in ALIASES:
        return f"❓ Unknown token `{token}` — try BTC, BNB, ETH, FLOKI, TOKENFI."

    cg_id, contract = ALIASES[token]

    # 1️⃣ Try CoinGecko
    try:
        r = requests.get(CG_URL.format(tid=cg_id), timeout=6)
        d = r.json()
        if cg_id in d:
            p = d[cg_id]["usd"]
            return f"💰 {token.upper()} price: ${p:,.6f}\n🕒 Source: CoinGecko"
    except Exception:
        pass

    # 2️⃣ Try DexScreener fallback
    try:
        r = requests.get(DEX_URL.format(contract=contract), timeout=6)
        d = r.json()
        if "pairs" in d and d["pairs"]:
            p = d["pairs"][0].get("priceUsd")
            if p:
                return f"💰 {token.upper()} price: ${float(p):,.6f}\n🕒 Source: DexScreener"
    except Exception:
        pass

    return f"⚠️ Could not fetch {token.upper()} price."

# === WALLET BALANCE ===
def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address.lower()}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=6).json()
        if res.get("status") != "1":
            return "❌ Invalid or inactive address."
        balance = int(res["result"]) / 1e18
        return f"{balance:.6f} BNB"
    except Exception:
        return "❌ Network/API timeout."

# === TOKEN SUPPLY ===
def get_token_supply(contract):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=6).json()
        if res.get("status") != "1":
            return "❌ Could not fetch (invalid/limit)."
        total = int(res["result"]) / 1e18
        return f"{total:,.0f} tokens"
    except Exception:
        return "❌ Supply fetch error."

# === TELEGRAM COMMANDS ===
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "╭─────────────🌐─────────────╮\n"
        "<b>WENBNB Web3 Command Center</b>\n"
        "╰────────────────────────────╯\n\n"
        "💰 /tokenprice <id> — Live token price\n"
        "👛 /wallet <address> — Wallet balance\n"
        "📊 /supply <contract> — Token total supply\n"
        "🧠 /analyze <address> — AI wallet risk (coming soon)\n\n"
        "✨ Hybrid Intelligence powered by <b>WENBNB Neural Engine</b>\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    token = context.args[0] if context.args else "bnb"
    msg = get_token_price(token)
    t = time.strftime("%H:%M:%S", time.localtime())
    update.message.reply_text(f"{msg}\n\n{BRAND_TAG}\n🕒 {t} (v5.8.2-ProPulse+ UIx)", parse_mode="HTML")

def wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_address>")
        return
    address = context.args[0]
    balance = get_wallet_balance(address)
    text = (
        "╭──────────👛──────────╮\n"
        f"<b>Wallet:</b>\n<code>{address}</code>\n"
        f"💎 Balance: <b>{balance}</b>\n"
        "╰──────────────────────╯\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract>")
        return
    contract = context.args[0]
    total = get_token_supply(contract)
    text = (
        "╭──────────📊──────────╮\n"
        f"<b>Token Supply</b>\n<code>{contract}</code>\n"
        f"Total: <b>{total}</b>\n"
        "╰──────────────────────╯\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def analyze(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /analyze <wallet_address>")
        return
    wallet = context.args[0]
    text = (
        "╭──────────🧠──────────╮\n"
        "<b>AI Wallet Risk Analysis</b>\n"
        "╰──────────────────────╯\n\n"
        f"🔍 Address: <code>{wallet}</code>\n\n"
        "📊 Scanning wallet activity, liquidity patterns, and token movements…\n"
        "💬 <i>Neural Risk Engine</i> is calibrating.\n\n"
        "⏳ <b>Coming Soon...</b>\n"
        "This module will detect risky wallets, analyze holding behavior, "
        "and rate confidence levels from ⚠️ Low → ✅ Safe.\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet))
    dp.add_handler(CommandHandler("supply", supply))
    dp.add_handler(CommandHandler("analyze", analyze))

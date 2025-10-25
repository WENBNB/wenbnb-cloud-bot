"""
WENBNB Web3 Connect v5.8.1-ProPulse+ Extended
───────────────────────────────────────────────────────────────
Enhanced version with wallet/supply fixes, polished analyze panel,
and modernized WENBNB design for Telegram interface.
💫 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡
"""

import requests, os, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
CMC_KEY = os.getenv("CMC_API_KEY", "")
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡"

# === API URLs ===
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}"
CG_URL = "https://api.coingecko.com/api/v3/simple/price?ids={tid}&vs_currencies=usd"
DEX_URL = "https://api.dexscreener.com/latest/dex/tokens/{contract}"
BSC_BASE = "https://api.bscscan.com/api"

# === TOKEN MAP ===
ALIASES = {
    "bnb": ("BNBUSDT", "binancecoin", "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"),
    "eth": ("ETHUSDT", "ethereum", "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"),
    "btc": ("BTCUSDT", "bitcoin", "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"),
    "doge": ("DOGEUSDT", "dogecoin", "0xbA2aE424d960c26247Dd6c32edC70B295c744C43"),
    "pepe": ("", "pepe", "0x6982508145454Ce325dDbE47a25d4ec3d2311933"),
    "floki": ("", "floki", "0xfb5b838b6cfeedc2873ab27866079ac55363d37e"),
    "tokenfi": ("", "tokenfi", "0x4507cEf57C46789eF8d1a19EA45f4216bae2B528"),
    "wenbnb": ("", "wenbnb", "0x4507cEf57C46789eF8d1a19EA45f4216bae2B528"),
}

# === PRICE ENGINE ===
def get_token_price(token: str):
    token = token.lower().strip()
    if token not in ALIASES:
        return f"❓ Unknown token `{token}` — try BTC, BNB, ETH, PEPE, FLOKI, TOKENFI."

    binance_symbol, coingecko_id, contract = ALIASES[token]

    # Binance
    if binance_symbol:
        try:
            r = requests.get(BINANCE_URL.format(symbol=binance_symbol), timeout=4)
            d = r.json()
            if "price" in d:
                p = float(d["price"])
                return f"💰 {token.upper()} price: ${p:,.4f}\n🕒 Source: Binance (Live)"
        except Exception as e:
            print(f"[Binance Error] {e}")

    # CoinGecko fallback
    try:
        r = requests.get(CG_URL.format(tid=coingecko_id), timeout=6)
        d = r.json()
        if coingecko_id in d:
            p = d[coingecko_id]["usd"]
            return f"💰 {token.upper()} price: ${p:,.6f}\n🕒 Source: CoinGecko"
    except Exception as e:
        print(f"[CG Error] {e}")

    # DexScreener fallback
    try:
        r = requests.get(DEX_URL.format(contract=contract), timeout=6)
        d = r.json()
        if "pairs" in d and d["pairs"]:
            p = d["pairs"][0].get("priceUsd")
            if p:
                return f"💰 {token.upper()} price: ${float(p):,.6f}\n🕒 Source: DexScreener"
    except Exception as e:
        print(f"[Dex Error] {e}")

    return f"⚠️ Unable to fetch {token.upper()} price right now."

def handle_tokenprice_command(token):
    msg = get_token_price(token)
    t = time.strftime("%H:%M:%S", time.localtime())
    return f"{msg}\n\n{BRAND_TAG}\n⏱️ {t} (v5.8.1-ProPulse+)"

# === WALLET BALANCE ===
def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        if res.get("status") != "1":
            return "❌ Invalid address or network issue."
        wei_balance = int(res.get("result", 0))
        bnb_balance = wei_balance / 1e18
        return f"{bnb_balance:.6f} BNB"
    except Exception as e:
        print(f"[Wallet Error] {e}")
        return "❌ Network or API error."

# === TOKEN SUPPLY ===
def get_token_supply(contract):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        if res.get("status") != "1":
            return "❌ Could not fetch token supply (API limit or invalid contract)."
        result = int(res.get("result", 0))
        return f"{result / 1e18:,.0f} tokens"
    except Exception as e:
        print(f"[Supply Error] {e}")
        return "❌ Could not fetch token supply."

# === COMMAND HANDLERS ===
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌐 <b>WENBNB Web3 Command Center</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💰 /tokenprice &lt;id&gt; — Live token price\n"
        "👛 /wallet &lt;address&gt; — Wallet balance\n"
        "📊 /supply &lt;contract&gt; — Token total supply\n"
        "🧠 /analyze &lt;address&gt; — AI wallet risk (coming soon)\n\n"
        "💫 Hybrid Intelligence powered by WENBNB Neural Engine\n"
        "──────────────────────────────\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    token = context.args[0] if context.args else "bnb"
    update.message.reply_text(handle_tokenprice_command(token), parse_mode="HTML")

def wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_address>")
        return
    address = context.args[0]
    balance = get_wallet_balance(address)
    text = (
        f"👛 <b>Wallet:</b>\n<code>{address}</code>\n\n"
        f"💎 Balance: <b>{balance}</b>\n\n{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    supply = get_token_supply(contract)
    text = (
        f"📊 <b>Token Supply</b>\n<code>{contract}</code>\n"
        f"Total: <b>{supply}</b>\n\n{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# === NEW ANALYZE PANEL (COMING SOON) ===
def analyze(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /analyze <wallet_address>")
        return
    wallet = context.args[0]
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 <b>AI Wallet Risk Analysis</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔍 Address: <code>{wallet}</code>\n\n"
        "📊 Scanning wallet activity, liquidity patterns, and token movements...\n"
        "💬 <i>Neural Risk Engine</i> is calibrating.\n\n"
        "⏳ <b>Coming Soon...</b>\n"
        "This module will detect risky wallets, analyze holding patterns, "
        "and rate confidence levels from ⚠️ Low → ✅ Safe.\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# === REGISTER COMMANDS ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet))
    dp.add_handler(CommandHandler("supply", supply))
    dp.add_handler(CommandHandler("analyze", analyze))

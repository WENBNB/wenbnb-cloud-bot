"""
WENBNB Web3 Connect v6.3-NeuralFeed Sync — Unified Web3 Command Center
──────────────────────────────────────────────────────────────────────────
Smart multi-source structure:
Binance → CoinGecko → DexScreener → fallback “coming soon” message.
💫 Powered by <b>WENBNB Neural Engine</b> — Web3 Intelligence 24×7 ⚡
"""

import requests, os, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
PLUGIN_NAME = "web3_connect"
BRAND_TAG = "🚀 <b>WENBNB Neural Engine</b> — Web3 Intelligence 24×7 ⚡"

# === API URLs ===
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
DEX_URL = "https://api.dexscreener.com/latest/dex/tokens/{contract}"
BSC_BASE = "https://api.bscscan.com/api"

# === COMMON TOKEN MAP ===
ALIASES = {
    "bnb": ("BNBUSDT", "binancecoin", "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"),
    "eth": ("ETHUSDT", "ethereum", "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"),
    "btc": ("BTCUSDT", "bitcoin", "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"),
    "doge": ("DOGEUSDT", "dogecoin", "0xbA2aE424d960c26247Dd6c32edC70B295c744C43"),
    "shib": ("SHIBUSDT", "shiba-inu", "0x285A8F15d05E1ECf4c77101c9A09d38F5B0f9F10"),
    "pepe": ("PEPEUSDT", "pepe", "0x6982508145454Ce325dDbE47a25d4ec3d2311933"),
    "bonk": ("", "bonk", "0x5c9fBDc73C708c04662D485fD6c4e6D92a9e9F43"),
    "trx": ("TRXUSDT", "tron", "0x50327c6c5a14DCaDE707abad2E27e8A6E6A6a7eB"),
    "xrp": ("XRPUSDT", "ripple", "0x1d2f0da169ceB9Fc7B3144628dB156f3F6f2f947"),
    "wenbnb": ("", "wenbnb", "0x4507cEf57C46789eF8d1a19EA45f4216bae2B528"),
}

# === PRICE FETCHER ===
def get_token_price(token: str):
    token = token.lower().strip()
    alias = ALIASES.get(token)

    if not alias:
        return f"⚠️ Unknown token <b>{token.upper()}</b> — not yet in NeuralFeed."

    binance_symbol, cg_id, contract = alias

    # 1️⃣ Binance
    if binance_symbol:
        try:
            r = requests.get(BINANCE_URL.format(symbol=binance_symbol), timeout=5).json()
            if "price" in r:
                p = float(r["price"])
                return f"💰 <b>{token.upper()} Price:</b> ${p:,.6f}\n📈 <b>Source:</b> Binance\n\n{BRAND_TAG}"
        except Exception:
            pass

    # 2️⃣ CoinGecko
    try:
        r = requests.get(COINGECKO_URL.format(id=cg_id), timeout=6).json()
        if cg_id in r:
            p = float(r[cg_id]["usd"])
            return f"💰 <b>{token.upper()} Price:</b> ${p:,.8f}\n📈 <b>Source:</b> CoinGecko\n\n{BRAND_TAG}"
    except Exception:
        pass

    # 3️⃣ DexScreener
    try:
        r = requests.get(DEX_URL.format(contract=contract), timeout=8).json()
        pairs = r.get("pairs", [])
        if pairs:
            p = float(pairs[0].get("priceUsd", 0))
            name = pairs[0].get("baseToken", {}).get("name", token.upper())
            return f"💰 <b>{name} ({token.upper()})</b>\n💎 <b>Price:</b> ${p:,.8f}\n📈 <b>Source:</b> DexScreener\n\n{BRAND_TAG}"
    except Exception:
        pass

    return f"⏳ <b>{token.upper()}</b> data syncing to NeuralFeed — coming soon 🚀\n\n{BRAND_TAG}"

def handle_tokenprice_command(token):
    msg = get_token_price(token)
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    return f"{msg}\n⏱️ <i>{timestamp}</i>"

# === WALLET BALANCE ===
def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        wei_balance = int(res.get("result", 0))
        bnb_balance = wei_balance / 1e18
        return f"{bnb_balance:.6f} BNB"
    except Exception:
        return "❌ Invalid address or network error."

# === TOKEN SUPPLY ===
def get_token_supply(contract):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        result = int(res.get("result", 0))
        return f"{result / 1e18:,.0f} tokens"
    except Exception:
        return "❌ Could not fetch token supply."

# === ANALYZE PLACEHOLDER ===
def analyze_wallet(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🧠 Neural Wallet Analyzer coming soon — will detect risk, volume, and whale patterns ⚡",
        parse_mode="HTML"
    )

# === WEB3 PANEL ===
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "🌐 <b>WENBNB Web3 Command Center</b>\n\n"
        "💰 <b>/tokenprice</b> <i>&lt;id&gt;</i> — Live token price\n"
        "👛 <b>/wallet</b> <i>&lt;address&gt;</i> — Wallet balance\n"
        "📊 <b>/supply</b> <i>&lt;contract&gt;</i> — Token supply\n"
        "🧠 <b>/analyze</b> — Wallet risk scan (coming soon)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# === COMMAND HANDLERS ===
def tokenprice(update: Update, context: CallbackContext):
    token = context.args[0] if context.args else "bnb"
    update.message.reply_text(handle_tokenprice_command(token), parse_mode="HTML")

def wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_address>")
        return
    address = context.args[0]
    balance = get_wallet_balance(address)
    text = f"👛 <b>Wallet:</b> <code>{address}</code>\n💎 <b>Balance:</b> <b>{balance}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    supply = get_token_supply(contract)
    text = f"📊 <b>Token Supply</b>\n<code>{contract}</code>\n💰 <b>Total:</b> <b>{supply}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet))
    dp.add_handler(CommandHandler("supply", supply))
    dp.add_handler(CommandHandler("analyze", analyze_wallet))
    print("✅ Loaded plugin: plugins.web3_connect (v6.3-NeuralFeed Sync)")

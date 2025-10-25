"""
WENBNB Web3 Connect v5.9-Pro Parallel Sync
──────────────────────────────────────────────
⚡ Smart Parallel Price Engine
⚙️ Binance → CoinMarketCap → CoinGecko → DexScreener
💎 Instant response (first API wins)
🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7
"""

import os, time, requests, concurrent.futures
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
DEX_URL = "https://api.dexscreener.com/latest/dex/search?q={q}"
BSC_BASE = "https://api.bscscan.com/api"

# === TOKEN MAP ===
ALIASES = {
    "bnb": ("BNBUSDT", "binancecoin", "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"),
    "eth": ("ETHUSDT", "ethereum", "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"),
    "btc": ("BTCUSDT", "bitcoin", "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"),
    "doge": ("DOGEUSDT", "dogecoin", "0xbA2aE424d960c26247Dd6c32edC70B295c744C43"),
    "wenbnb": ("", "wenbnb", "0x4507cEf57C46789eF8d1a19EA45f4216bae2B528"),
}

# === PARALLEL PRICE FETCHERS ===
def fetch_binance(token, binance_symbol):
    try:
        if not binance_symbol:
            return None
        res = requests.get(BINANCE_URL.format(symbol=binance_symbol), timeout=4)
        data = res.json()
        if "price" in data:
            return (float(data["price"]), "Binance (Live)")
    except Exception:
        return None

def fetch_cmc(token):
    if not CMC_KEY:
        return None
    try:
        headers = {"X-CMC_PRO_API_KEY": CMC_KEY}
        res = requests.get(CMC_URL.format(symbol=token.upper()), headers=headers, timeout=5)
        data = res.json()
        if "data" in data and token.upper() in data["data"]:
            price = data["data"][token.upper()]["quote"]["USD"]["price"]
            return (price, "CoinMarketCap")
    except Exception:
        return None

def fetch_coingecko(cgid):
    try:
        res = requests.get(CG_URL.format(tid=cgid), timeout=5)
        data = res.json()
        if cgid in data:
            return (data[cgid]["usd"], "CoinGecko")
    except Exception:
        return None

def fetch_dex(contract_or_query):
    try:
        res = requests.get(DEX_URL.format(q=contract_or_query), timeout=6)
        data = res.json()
        if "pairs" in data and data["pairs"]:
            p = data["pairs"][0]
            return (float(p["priceUsd"]), f"DexScreener ({p['dexId']})")
    except Exception:
        return None

# === PRICE FETCH CONTROLLER ===
def get_token_price(token: str):
    token = token.lower().strip()
    if token not in ALIASES:
        return f"❓ Unknown token <b>{token.upper()}</b>\n🪄 WENBNB Neural Feed learning new assets..."

    binance_symbol, coingecko_id, contract = ALIASES[token]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_binance, token, binance_symbol),
            executor.submit(fetch_cmc, token),
            executor.submit(fetch_coingecko, coingecko_id),
            executor.submit(fetch_dex, contract),
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                price, source = result
                return f"💰 <b>{token.upper()}</b> current price: <b>${price:,.6f}</b>\n🕒 Source: {source}"

    return f"⚠️ Unable to fetch <b>{token.upper()}</b> price.\nPlease retry later."

# === WALLET BALANCE ===
def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=6).json()
        wei = int(res.get("result", 0))
        return f"{wei / 1e18:.6f} BNB"
    except Exception:
        return "❌ Invalid or unreachable address."

# === TOKEN SUPPLY ===
def get_token_supply(contract):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=6).json()
        supply = int(res.get("result", 0)) / 1e18
        return f"{supply:,.0f} tokens"
    except Exception:
        return "❌ Unable to fetch token supply."

# === ANALYZE PLACEHOLDER ===
def analyze_placeholder():
    return (
        "🧠 <b>WENBNB Wallet Intelligence (Coming Soon)</b>\n"
        "AI-based wallet scanner detecting:\n"
        "• Risk & wash trading patterns\n"
        "• Whale wallet activity\n"
        "• Contract risk levels\n"
        "• Profit/loss analytics\n\n"
        "💫 Launching in Pro Mode v8.1!"
    )

# === COMMAND HANDLERS ===
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "🌐 <b>WENBNB Web3 Command Center</b>\n\n"
        "💰 /tokenprice <id> — Live token price\n"
        "👛 /wallet <address> — Wallet balance\n"
        "📊 /supply <contract> — Token total supply\n"
        "🧠 /analyze <address> — AI wallet risk (coming soon)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    token = context.args[0] if context.args else "wenbnb"
    msg = get_token_price(token)
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    update.message.reply_text(f"{msg}\n\n{BRAND_TAG}\n⏱️ {timestamp}", parse_mode="HTML")

def wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_address>")
        return
    address = context.args[0]
    bal = get_wallet_balance(address)
    update.message.reply_text(f"👛 <b>Wallet:</b> <code>{address}</code>\n💎 Balance: <b>{bal}</b>\n\n{BRAND_TAG}", parse_mode="HTML")

def supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    total = get_token_supply(contract)
    update.message.reply_text(f"📊 <b>Token Supply</b>\n<code>{contract}</code>\nTotal: <b>{total}</b>\n\n{BRAND_TAG}", parse_mode="HTML")

def analyze(update: Update, context: CallbackContext):
    update.message.reply_text(analyze_placeholder(), parse_mode="HTML")

def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet))
    dp.add_handler(CommandHandler("supply", supply))
    dp.add_handler(CommandHandler("analyze", analyze))
    print("✅ Loaded plugin: web3_connect (v5.9-Pro Parallel Sync)")

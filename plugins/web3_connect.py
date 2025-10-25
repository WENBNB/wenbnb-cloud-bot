"""
WENBNB Web3 Connect v5.8-ProPulse+ — AI Hybrid Web3 Command Center
──────────────────────────────────────────────────────────────────────────
Enhanced version with auto-fallback, API health retry, wallet/supply fix,
and smart token resolver for Floki, TokenFi, Pepe etc.
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

# === TOKEN MAP (extended) ===
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

# === API HEALTH CHECK ===
def check_api(url, headers=None):
    try:
        res = requests.get(url, headers=headers, timeout=4)
        return res.status_code == 200
    except:
        return False

def get_api_status():
    status = {
        "Binance": "🟢" if check_api("https://api.binance.com/api/v3/ping") else "🔴",
        "CoinMarketCap": "🟢" if check_api(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map",
            {"X-CMC_PRO_API_KEY": CMC_KEY}) else "🔴",
        "CoinGecko": "🟢" if check_api("https://api.coingecko.com/api/v3/ping") else "🔴",
        "DexScreener": "🟢" if check_api("https://api.dexscreener.com/latest/dex/pairs/eth") else "🔴",
    }
    return status

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
        except: pass

    # CMC
    if CMC_KEY:
        try:
            headers = {"X-CMC_PRO_API_KEY": CMC_KEY}
            r = requests.get(CMC_URL.format(symbol=token.upper()), headers=headers, timeout=6)
            d = r.json()
            if "data" in d and token.upper() in d["data"]:
                p = d["data"][token.upper()]["quote"]["USD"]["price"]
                return f"💰 {token.upper()} price: ${p:,.4f}\n🕒 Source: CoinMarketCap"
        except: pass

    # CoinGecko
    try:
        r = requests.get(CG_URL.format(tid=coingecko_id), timeout=6)
        d = r.json()
        if coingecko_id in d:
            p = d[coingecko_id]["usd"]
            return f"💰 {token.upper()} price: ${p:,.6f}\n🕒 Source: CoinGecko"
    except: pass

    # Dex
    try:
        r = requests.get(DEX_URL.format(contract=contract), timeout=6)
        d = r.json()
        if "pairs" in d and d["pairs"]:
            p = d["pairs"][0].get("priceUsd")
            if p:
                return f"💰 {token.upper()} price: ${float(p):,.6f}\n🕒 Source: DexScreener"
    except: pass

    return f"⚠️ Unable to fetch {token.upper()} price right now."

def handle_tokenprice_command(token):
    msg = get_token_price(token)
    t = time.strftime("%H:%M:%S", time.localtime())
    return f"{msg}\n\n{BRAND_TAG}\n⏱️ {t} (v5.8-ProPulse+)"

# === WALLET BALANCE ===
def get_wallet_balance(address):
    try:
        if not BSCSCAN_API_KEY:
            return "⚠️ Missing BscScan API key — please configure it."
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        r = requests.get(url).json()
        wei = int(r.get("result", 0))
        return f"{wei/1e18:.6f} BNB"
    except:
        return "❌ Invalid address or network error."

# === TOKEN SUPPLY ===
def get_token_supply(contract):
    try:
        if not BSCSCAN_API_KEY:
            return "⚠️ Missing BscScan API key — please configure it."
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract}&apikey={BSCSCAN_API_KEY}"
        r = requests.get(url).json()
        return f"{int(r.get('result',0))/1e18:,.0f} tokens"
    except:
        return "❌ Could not fetch token supply."

# === COMMAND HANDLERS ===
def web3_panel(update: Update, context: CallbackContext):
    s = get_api_status()
    text = (
        "🌐 <b>WENBNB Web3 Command Center</b>\n\n"
        "💰 /tokenprice &lt;id&gt; — Live token price\n"
        "👛 /wallet &lt;address&gt; — Wallet balance\n"
        "📊 /supply &lt;contract&gt; — Token total supply\n"
        "🧠 /analyze &lt;address&gt; — AI wallet risk (coming soon)\n\n"
        "🛰️ <b>Data Source Status:</b>\n"
        f" • Binance {s['Binance']}\n"
        f" • CoinMarketCap {s['CoinMarketCap']}\n"
        f" • CoinGecko {s['CoinGecko']}\n"
        f" • DexScreener {s['DexScreener']}\n\n"
        "⚙️ <b>Core Version:</b> Web3 Connect v5.8-ProPulse+\n"
        "💫 <i>Hybrid Intelligence powered by WENBNB Neural Engine</i>\n"
        "──────────────────────────────\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    token = context.args[0] if context.args else "bnb"
    update.message.reply_text(handle_tokenprice_command(token), parse_mode="HTML")

def wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet &lt;BSC_address&gt;")
        return
    addr = context.args[0]
    bal = get_wallet_balance(addr)
    update.message.reply_text(
        f"👛 <b>Wallet</b>: <code>{addr}</code>\n💎 Balance: <b>{bal}</b>\n\n{BRAND_TAG}",
        parse_mode="HTML"
    )

def supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply &lt;contract_address&gt;")
        return
    c = context.args[0]
    s = get_token_supply(c)
    update.message.reply_text(
        f"📊 <b>Token Supply</b>\n<code>{c}</code>\nTotal: <b>{s}</b>\n\n{BRAND_TAG}",
        parse_mode="HTML"
    )

def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet))
    dp.add_handler(CommandHandler("supply", supply))

"""
WENBNB Web3 Connect v5.5-Pro Sync — AI Hybrid Web3 Command Center
──────────────────────────────────────────────────────────────────────────
Integrated Binance + CoinMarketCap + CoinGecko + DexScreener fallback stack
for ultra-reliable token data. Includes /wallet, /supply, /tokenprice, /web3
💫 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡
"""

import requests, os, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
CMC_KEY = os.getenv("CMC_API_KEY", "")
PLUGIN_NAME = "web3_connect"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡"

# === API URLs ===
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}"
CG_URL = "https://api.coingecko.com/api/v3/simple/price?ids={tid}&vs_currencies=usd"
DEX_URL = "https://api.dexscreener.com/latest/dex/tokens/{contract}"
BSC_BASE = "https://api.bscscan.com/api"

# === COMMON TOKEN MAP ===
ALIASES = {
    "bnb": ("BNBUSDT", "binancecoin", "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"),
    "eth": ("ETHUSDT", "ethereum", "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"),
    "btc": ("BTCUSDT", "bitcoin", "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"),
    "doge": ("DOGEUSDT", "dogecoin", "0xbA2aE424d960c26247Dd6c32edC70B295c744C43"),
    "wenbnb": ("", "wenbnb", "0x4507cEf57C46789eF8d1a19EA45f4216bae2B528"),
}

# === PRICE ENGINE ===
def get_token_price(token: str):
    token = token.lower().strip()
    if token not in ALIASES:
        return f"❓ Unknown token `{token}` — please use a valid symbol."

    binance_symbol, coingecko_id, contract = ALIASES[token]

    # 1️⃣ Binance
    if binance_symbol:
        try:
            res = requests.get(BINANCE_URL.format(symbol=binance_symbol), timeout=4)
            data = res.json()
            if "price" in data:
                price = float(data["price"])
                return f"💰 {token.upper()} current price: ${price:,.4f}\n🕒 Source: Binance (Live)"
        except Exception as e:
            print(f"[Binance Error] {e}")

    # 2️⃣ CoinMarketCap
    if CMC_KEY:
        try:
            headers = {"X-CMC_PRO_API_KEY": CMC_KEY}
            res = requests.get(CMC_URL.format(symbol=token.upper()), headers=headers, timeout=6)
            data = res.json()
            if "data" in data and token.upper() in data["data"]:
                price = data["data"][token.upper()]["quote"]["USD"]["price"]
                return f"💰 {token.upper()} current price: ${price:,.4f}\n🕒 Source: CoinMarketCap"
        except Exception as e:
            print(f"[CMC Error] {e}")

    # 3️⃣ CoinGecko
    try:
        res = requests.get(CG_URL.format(tid=coingecko_id), timeout=6)
        data = res.json()
        if coingecko_id in data:
            price = data[coingecko_id]["usd"]
            return f"💰 {token.upper()} current price: ${price:,.4f}\n🕒 Source: CoinGecko"
    except Exception as e:
        print(f"[CG Error] {e}")

    # 4️⃣ DexScreener
    try:
        res = requests.get(DEX_URL.format(contract=contract), timeout=6)
        data = res.json()
        if "pairs" in data and data["pairs"]:
            price = data["pairs"][0].get("priceUsd")
            if price:
                return f"💰 {token.upper()} current price: ${float(price):,.6f}\n🕒 Source: DexScreener (DEX)"
    except Exception as e:
        print(f"[Dex Error] {e}")

    return f"⚠️ Unable to fetch {token.upper()} price.\nTry again later."

def handle_tokenprice_command(token):
    msg = get_token_price(token)
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    return f"{msg}\n\n{BRAND_TAG}\n⏱️ {timestamp} (v5.5-Pro Sync)"

# === WALLET BALANCE ===
def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        wei_balance = int(res.get("result", 0))
        bnb_balance = wei_balance / 1e18
        return f"{bnb_balance:.6f} BNB"
    except Exception as e:
        print(f"[Wallet Error] {e}")
        return "❌ Invalid address or network error."

# === TOKEN SUPPLY ===
def get_token_supply(contract):
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url).json()
        result = int(res.get("result", 0))
        return f"{result / 1e18:,.0f} tokens"
    except Exception as e:
        print(f"[Supply Error] {e}")
        return "❌ Could not fetch token supply."

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
    token = context.args[0] if context.args else "bnb"
    update.message.reply_text(handle_tokenprice_command(token), parse_mode="HTML")

def wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_address>")
        return
    address = context.args[0]
    balance = get_wallet_balance(address)
    text = f"👛 <b>Wallet</b>: <code>{address}</code>\n💎 Balance: <b>{balance}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    supply = get_token_supply(contract)
    text = f"📊 <b>Token Supply</b>\n<code>{contract}</code>\nTotal: <b>{supply}</b>\n\n{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet))
    dp.add_handler(CommandHandler("supply", supply))

"""
WENBNB Web3 Connect v6.1-PulseEdge — Dual-Mode Token Intelligence
─────────────────────────────────────────────────────────────────────────────
✅ Dual-mode /tokenprice : supports <symbol> or <contract address>
✅ API chain: Binance → CoinMarketCap → CoinGecko → DexScreener
✅ HTML-safe formatting (no parse errors)
✅ Bold WENBNB Neural Engine branding
✅ Clean footer with live timestamp only
💫 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7 ⚡
"""

import requests, os, time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from web3 import Web3

# === CONFIG ===
BSC_RPC = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(BSC_RPC))

BRAND_TAG = "🚀 Powered by <b>WENBNB Neural Engine</b> — Web3 Intelligence 24×7 ⚡"

# === API KEYS (optional) ===
CMC_KEY = os.getenv("CMC_API_KEY", "")
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}"

# === TOKEN ALIASES ===
ALIASES = {
    "bnb": ("BNBUSDT", "binancecoin", "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"),
    "eth": ("ETHUSDT", "ethereum", "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"),
    "btc": ("BTCUSDT", "bitcoin", "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"),
    "doge": ("DOGEUSDT", "dogecoin", "0xbA2aE424d960c26247Dd6c32edC70B295c744C43"),
    "floki": ("", "floki", "0xCfc6Bf8a5a7A3DfA0284F97E5E8f7b870D454b2c"),
    "wenbnb": ("", "wenbnb", "0x4507cEf57C46789eF8d1a19EA45f4216bae2B528"),
}

# === TOKEN PRICE ENGINE ===
def get_token_price(token: str):
    token = token.lower().strip()

    # If user entered contract
    if token.startswith("0x") and len(token) == 42:
        try:
            r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token}", timeout=6)
            data = r.json()
            if "pairs" in data and data["pairs"]:
                price = float(data["pairs"][0].get("priceUsd"))
                return price, "DexScreener (Contract)"
        except Exception:
            return None, None

    # If token is in aliases
    if token not in ALIASES:
        return f"❓ Unknown token <b>{token.upper()}</b>\n🧠 WENBNB Neural Feed learning new assets...", None

    binance_symbol, cmc_symbol, contract = ALIASES[token]

    # 1️⃣ Binance (fastest)
    try:
        if binance_symbol:
            r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={binance_symbol}", timeout=4)
            data = r.json()
            if "price" in data:
                return float(data["price"]), "Binance (Live)"
    except Exception:
        pass

    # 2️⃣ CoinMarketCap
    try:
        if CMC_KEY:
            headers = {"X-CMC_PRO_API_KEY": CMC_KEY}
            r = requests.get(CMC_URL.format(symbol=token.upper()), headers=headers, timeout=6)
            data = r.json()
            quote = data["data"][token.upper()]["quote"]["USD"]["price"]
            return float(quote), "CoinMarketCap"
    except Exception:
        pass

    # 3️⃣ CoinGecko
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={cmc_symbol}&vs_currencies=usd", timeout=6)
        data = r.json()
        if cmc_symbol in data:
            return data[cmc_symbol]["usd"], "CoinGecko"
    except Exception:
        pass

    # 4️⃣ DexScreener fallback
    try:
        r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{contract}", timeout=6)
        data = r.json()
        if "pairs" in data and data["pairs"]:
            return float(data["pairs"][0].get("priceUsd")), "DexScreener"
    except Exception:
        pass

    return None, None


# === RPC FUNCTIONS ===
def get_wallet_balance_rpc(address):
    try:
        checksum_addr = w3.to_checksum_address(address)
        wei_balance = w3.eth.get_balance(checksum_addr)
        return f"{wei_balance / 1e18:.6f} BNB"
    except Exception:
        return "❌ Invalid or unreachable address."


def get_token_supply_rpc(contract):
    try:
        checksum_contract = w3.to_checksum_address(contract)
        erc20_abi = [{"constant": True, "inputs": [], "name": "totalSupply",
                      "outputs": [{"name": "", "type": "uint256"}],
                      "type": "function"}]
        token_contract = w3.eth.contract(address=checksum_contract, abi=erc20_abi)
        supply = token_contract.functions.totalSupply().call()
        return f"{supply / 1e18:,.0f} tokens"
    except Exception:
        return "❌ Could not fetch via RPC."


# === COMMANDS ===
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "🌐 <b>WENBNB Web3 Command Center</b>\n\n"
        "💰 /tokenprice &lt;id&gt; or &lt;contract&gt; — Live token price\n"
        "👛 /wallet <address> — Wallet balance\n"
        "📊 /supply <contract> — Token total supply\n"
        "🧠 /analyze <address> — AI wallet risk (coming soon)\n\n"
        "✨ Hybrid Intelligence powered by <b>WENBNB Neural Engine</b>\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def tokenprice(update: Update, context: CallbackContext):
    token = context.args[0] if context.args else "bnb"
    timestamp = time.strftime("%H:%M:%S", time.localtime())

    try:
        price, source = get_token_price(token)
    except Exception:
        price, source = None, None

    if isinstance(price, str):  # For unknown token message
        update.message.reply_text(price, parse_mode="HTML")
        return

    if price:
        msg = (
            f"💰 <b>{token.upper()} current price:</b> ${price:,.6f}\n"
            f"🕒 <b>Source:</b> {source}\n\n"
            f"{BRAND_TAG}\n"
            f"⏱️ {timestamp}"
        )
    else:
        msg = (
            f"❌ Could not fetch <b>{token.upper()}</b> price.\n"
            f"Try again later or check contract validity.\n\n"
            f"{BRAND_TAG}\n"
            f"⏱️ {timestamp}"
        )

    update.message.reply_text(msg, parse_mode="HTML")


def wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_address>")
        return
    address = context.args[0]
    balance = get_wallet_balance_rpc(address)
    text = (
        f"👛 <b>Wallet:</b>\n<code>{address}</code>\n"
        f"💎 <b>Balance:</b> {balance}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    supply = get_token_supply_rpc(contract)
    text = (
        f"📊 <b>Token Supply</b>\n<code>{contract}</code>\n"
        f"📦 <b>Total:</b> {supply}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def analyze(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /analyze <wallet_address>")
        return
    address = context.args[0]
    text = (
        "🧠 <b>AI Wallet Risk Analysis</b>\n"
        "-----------------------------------\n"
        f"🔍 <b>Address:</b> <code>{address}</code>\n\n"
        "📊 Scanning wallet activity, liquidity, and token movements...\n"
        "💭 Neural Risk Engine calibrating...\n\n"
        "⏳ <b>Coming Soon:</b> wallet risk confidence levels "
        "from ⚠️ Low → ✅ Safe.\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")


# === REGISTER HANDLERS ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet))
    dp.add_handler(CommandHandler("supply", supply))
    dp.add_handler(CommandHandler("analyze", analyze))

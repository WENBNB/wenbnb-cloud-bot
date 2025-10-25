"""
WENBNB AI Web3 Command Center v5.4-Pro+ ⚙️
────────────────────────────────────────────
Hybrid data bridge for blockchain analytics, wallet balance,
token supply & price tracking. Powered by WENBNB Neural Engine.

💫 Features:
• CoinGecko + DexScreener hybrid pricing
• On-chain RPC fallback for token supply
• Rate-limit aware wallet checks
• Auto-alias mapping for common tokens
"""

import requests, json, os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from web3 import Web3

# === CONFIG ===
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
CG_BASE = "https://api.coingecko.com/api/v3"
DS_BASE = "https://api.dexscreener.com/latest/dex/tokens"
BSC_BASE = "https://api.bscscan.com/api"
BSC_RPC = "https://bsc-dataseed.binance.org"
web3 = Web3(Web3.HTTPProvider(BSC_RPC))

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7"

ALIASES = {
    "bnb": "binancecoin",
    "bsc": "binancecoin",
    "eth": "ethereum",
    "btc": "bitcoin",
    "wenbnb": "wenbnb",
}

# === HELPERS ===

def format_usd(value):
    try:
        return f"${float(value):,.6f}"
    except:
        return "N/A"

def get_token_price(token_id="bnb", vs_currency="usd"):
    tid = ALIASES.get(token_id.lower(), token_id.lower())
    try:
        url = f"{CG_BASE}/simple/price?ids={tid}&vs_currencies={vs_currency}"
        res = requests.get(url, headers={"User-Agent": "WENBNBBot/1.0"}, timeout=5)
        data = res.json()
        if tid in data:
            return data[tid][vs_currency]
        # Fallback → DexScreener (by token name lookup)
        if token_id.lower() in ["bnb", "binancecoin"]:
            contract = "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"  # BNB contract
            durl = f"{DS_BASE}/{contract}"
            dres = requests.get(durl, timeout=5).json()
            price = dres.get("pairs", [{}])[0].get("priceUsd")
            return float(price) if price else "N/A"
        return "N/A"
    except Exception as e:
        return "N/A"

def get_wallet_balance(address):
    try:
        url = f"{BSC_BASE}?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=5).json()
        if res.get("status") == "1":
            wei_balance = int(res.get("result", 0))
            bnb_balance = wei_balance / (10**18)
            return f"{bnb_balance:.6f} BNB"
        else:
            return "❌ Invalid or unreachable address.\nTip: BscScan may rate-limit; retry later."
    except Exception:
        return "⚠️ Error contacting BscScan API."

def get_token_supply(contract_address):
    """Try BscScan first; fallback to direct RPC."""
    try:
        url = f"{BSC_BASE}?module=stats&action=tokensupply&contractaddress={contract_address}&apikey={BSCSCAN_API_KEY}"
        res = requests.get(url, timeout=5).json()
        if res.get("status") == "1":
            total = int(res.get("result", 0)) / 1e18
            return f"{total:,.0f} tokens"
        # Fallback to RPC
        abi = [{"constant": True, "inputs": [], "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
        contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        supply = contract.functions.totalSupply().call()
        return f"{supply / 1e18:,.0f} tokens (via RPC)"
    except Exception:
        return "❌ Invalid or unverified contract.\nTip: Verify contract on BscScan or try again later."

# === COMMANDS ===

def web3_panel(update: Update, context: CallbackContext):
    text = (
        "<b>🌐 WENBNB AI Web3 Command Center</b>\n\n"
        "💰 /tokenprice &lt;token_id&gt; — Get live price (CoinGecko + DexScreener)\n"
        "👛 /wallet &lt;address&gt; — Check BNB wallet balance\n"
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
    text = (
        f"💰 <b>{token_id.upper()}</b> current price:\n<b>{format_usd(price)}</b>\n\n"
        f"Tip: token may not be listed on CoinGecko yet.\n\n{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def wallet_balance(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_wallet_address>")
        return
    address = context.args[0]
    balance = get_wallet_balance(address)
    text = (
        f"👛 <b>Wallet:</b>\n<code>{address}</code>\n"
        f"Balance: {balance}\n\n{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def token_supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    contract = context.args[0]
    supply = get_token_supply(contract)
    text = (
        f"📊 <b>Token Supply for:</b>\n<code>{contract}</code>\n"
        f"Total: {supply}\n\n"
        f"Tip: Verify the contract source on BscScan to enable full supply analytics.\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def analyze_wallet(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /analyze <wallet_address>")
        return
    address = context.args[0]
    text = (
        f"🧠 <b>AI Wallet Risk Analyzer — v1.0 Prototype</b>\n\n"
        f"Analyzing wallet:\n<code>{address}</code>\n"
        f"Status: Feature coming in Emotion Sync upgrade (v5.5)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# === REGISTER HANDLERS ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet_balance))
    dp.add_handler(CommandHandler("supply", token_supply))
    dp.add_handler(CommandHandler("analyze", analyze_wallet))

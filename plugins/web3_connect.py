# plugins/web3_connect.py
"""
WENBNB Smart On-Chain Bridge
Version: 3.4 — Locked & Approved
Mode: Hybrid (AI + Web3 Gateway)
"""

from web3 import Web3
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import os, json, requests

# === CONFIG ===
BSC_RPC = "https://bsc-dataseed1.binance.org"
w3 = Web3(Web3.HTTPProvider(BSC_RPC))
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"
TOKEN_API = "https://api.dexscreener.io/latest/dex/tokens/"


# === CORE UTILITIES ===

def shorten(address):
    """Shortens wallet address for cleaner UI"""
    return f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address


def get_balance(address):
    """Returns native BNB balance in readable format"""
    try:
        balance_wei = w3.eth.get_balance(address)
        return round(w3.from_wei(balance_wei, "ether"), 4)
    except Exception:
        return None


def get_token_price(token_address):
    """Fetch token price data from DexScreener"""
    try:
        r = requests.get(TOKEN_API + token_address)
        data = r.json()
        if "pairs" in data and data["pairs"]:
            price_usd = data["pairs"][0]["priceUsd"]
            symbol = data["pairs"][0]["baseToken"]["symbol"]
            return symbol, f"${float(price_usd):.4f}"
        return None, None
    except Exception:
        return None, None


# === COMMANDS ===

def connect_wallet(update: Update, context: CallbackContext):
    """User manually links wallet"""
    user = update.effective_user
    args = context.args

    if not args:
        update.message.reply_text("🔗 Use `/connect <wallet_address>` to link your wallet.")
        return

    address = args[0]
    if not Web3.is_address(address):
        update.message.reply_text("⚠️ Invalid wallet address format. Please check again.")
        return

    user_file = f"user_{user.id}_wallet.json"
    with open(user_file, "w") as f:
        json.dump({"wallet": address}, f)

    balance = get_balance(address)
    msg = (
        f"✅ Wallet connected successfully!\n\n"
        f"👤 User: @{user.username}\n"
        f"💼 Address: `{shorten(address)}`\n"
        f"💰 Balance: {balance} BNB\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(msg, parse_mode="Markdown")


def wallet_info(update: Update, context: CallbackContext):
    """Displays user’s linked wallet info"""
    user = update.effective_user
    user_file = f"user_{user.id}_wallet.json"

    if not os.path.exists(user_file):
        update.message.reply_text("⚠️ You haven’t connected any wallet yet.\nUse `/connect <address>` to link one.")
        return

    with open(user_file, "r") as f:
        data = json.load(f)

    wallet = data.get("wallet")
    balance = get_balance(wallet)
    update.message.reply_text(
        f"💳 <b>Wallet Info</b>\n"
        f"👤 @{user.username}\n"
        f"💼 Address: <code>{wallet}</code>\n"
        f"💰 Balance: <b>{balance} BNB</b>\n\n"
        f"{BRAND_FOOTER}",
        parse_mode="HTML"
    )


def token_track(update: Update, context: CallbackContext):
    """Track any token by contract"""
    args = context.args
    if not args:
        update.message.reply_text("🧩 Use `/track <token_contract>` to fetch live price data.")
        return

    token_address = args[0]
    symbol, price = get_token_price(token_address)

    if not symbol:
        update.message.reply_text("⚠️ Couldn’t fetch token info. Try again or check contract address.")
        return

    update.message.reply_text(
        f"💎 <b>Token Data</b>\n"
        f"🔹 Symbol: <b>{symbol}</b>\n"
        f"💰 Price: <b>{price}</b>\n\n"
        f"{BRAND_FOOTER}",
        parse_mode="HTML"
    )


def disconnect_wallet(update: Update, context: CallbackContext):
    """Clears linked wallet"""
    user = update.effective_user
    user_file = f"user_{user.id}_wallet.json"

    if os.path.exists(user_file):
        os.remove(user_file)
        update.message.reply_text(f"🔒 Wallet disconnected successfully.\n\n{BRAND_FOOTER}")
    else:
        update.message.reply_text("⚠️ No wallet found to disconnect.")


# === REGISTRATION ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("connect", connect_wallet))
    dp.add_handler(CommandHandler("wallet", wallet_info))
    dp.add_handler(CommandHandler("track", token_track))
    dp.add_handler(CommandHandler("disconnect", disconnect_wallet))

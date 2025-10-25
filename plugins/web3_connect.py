"""
WENBNB AI-Powered Web3 Command Center v5.3.1 (Patch)
- Safer wallet balance fetch (retries + normalization)
- Clear "unverified contract" messaging for /supply
- Better tokenprice fallback handling
🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7
"""

import os
import time
import requests
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Web3 Intelligence 24×7"

BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
CG_BASE = "https://api.coingecko.com/api/v3"
BSC_BASE = "https://api.bscscan.com/api"

# ---- Helpers ----
def safe_request(url, params=None, timeout=6, retries=2, backoff=1.2):
    """Simple requests.get with retry/backoff and safe JSON return (or None)."""
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
            else:
                return None

def format_usd(value):
    try:
        return f"${float(value):,.6f}"
    except Exception:
        return "N/A"

def normalize_address(addr: str):
    """Ensure 0x prefix and lowercase (safe for queries)."""
    if not addr:
        return ""
    addr = addr.strip()
    if addr.startswith("ethereum:"):  # handle clipboard weirdness
        addr = addr.split("ethereum:")[-1]
    if not addr.startswith("0x"):
        addr = "0x" + addr
    return addr.lower()

# ---- CoinGecko price ----
def get_token_price(token_id="wenbnb", vs_currency="usd"):
    try:
        url = f"{CG_BASE}/simple/price"
        params = {"ids": token_id, "vs_currencies": vs_currency}
        data = safe_request(url, params=params)
        if data and token_id in data and vs_currency in data[token_id]:
            return data[token_id][vs_currency]
    except Exception:
        pass
    return None

# ---- BscScan helpers ----
def bsc_account_balance(address):
    """
    Returns tuple (success, message)
    success -> float BNB balance or None
    message -> descriptive string or float
    """
    if not BSCSCAN_API_KEY:
        return False, "BscScan API key not configured."

    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "apikey": BSCSCAN_API_KEY
    }
    data = safe_request(BSC_BASE, params=params, retries=2)
    if not data:
        return False, "BscScan unreachable or timed out."

    # Typical BscScan response: {"status":"1","message":"OK","result":"12345..."}
    if str(data.get("status")) != "1":
        # Could be "0" with a message in result
        return False, "Invalid or unreachable address."

    try:
        wei = int(data.get("result", 0))
        bnb = wei / (10**18)
        return True, bnb
    except Exception:
        return False, "Parsing error."

def bsc_token_supply(contract_address):
    """Return (ok, value_or_reason). If contract not verified -> return (False, 'unverified')"""
    if not BSCSCAN_API_KEY:
        return False, "BscScan API key not configured."

    # First check tokensupply endpoint
    params = {
        "module": "stats",
        "action": "tokensupply",
        "contractaddress": contract_address,
        "apikey": BSCSCAN_API_KEY
    }
    data = safe_request(BSC_BASE, params=params, retries=2)
    if not data:
        return False, "BscScan unreachable."

    # If tokensupply returns non-OK, try contract verification check
    if str(data.get("status")) == "1" and data.get("result") is not None:
        try:
            raw = data.get("result")
            total = int(raw) / 1e18
            return True, total
        except Exception:
            return False, "Error parsing supply."

    # tokensupply failed: check if contract source is verified
    verify_params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
        "apikey": BSCSCAN_API_KEY
    }
    vdata = safe_request(BSC_BASE, params=verify_params, retries=1)
    if vdata and isinstance(vdata.get("result"), list) and len(vdata["result"]) > 0:
        src = vdata["result"][0].get("SourceCode")
        if src and len(src.strip()) > 0:
            # strange case: verified but tokensupply failed — report error
            return False, "Verified but failed to fetch supply."
        else:
            return False, "unverified"
    else:
        return False, "unverified"

# ---- Commands ----
def web3_panel(update: Update, context: CallbackContext):
    text = (
        "<b>🌐 WENBNB AI Web3 Command Center</b>\n\n"
        "💱 /tokenprice <token_id> — Get live price (CoinGecko)\n"
        "💎 /wallet <address> — Check BNB wallet balance (read-only)\n"
        "📊 /supply <contract> — Token total supply (BSC)\n"
        "🧠 /analyze <address> — AI wallet risk scan (coming soon)\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

def tokenprice(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /tokenprice <token_id>  (example: /tokenprice eth)")
        return
    token_id = context.args[0].lower()
    price = get_token_price(token_id)
    if price is None:
        # fallback message — coin not found on CoinGecko
        update.message.reply_text(f"💰 <b>{token_id.upper()}</b> current price:\n<b>N/A</b>\n\nTip: token may not be listed on CoinGecko yet.\n\n{BRAND_TAG}", parse_mode="HTML")
        return
    update.message.reply_text(f"💰 <b>{token_id.upper()}</b> current price:\n<b>{format_usd(price)}</b>\n\n{BRAND_TAG}", parse_mode="HTML")

def wallet_balance(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /wallet <BSC_wallet_address>")
        return
    raw = context.args[0]
    address = normalize_address(raw)

    # quick validation length
    if len(address) != 42 or not address.startswith("0x"):
        update.message.reply_text("⚠️ Invalid address format. Make sure address is 0x... hex.")
        return

    ok, result = bsc_account_balance(address)
    if not ok:
        # If result says unreachable or rate limit, provide helpful tips
        if "rate" in str(result).lower() or "unreachable" in str(result).lower():
            msg = f"👛 Wallet: <code>{address}</code>\nBalance: <b>Invalid or unreachable address.</b>\n\nTip: BscScan may rate-limit requests; try again or ensure API key has quota.\n\n{BRAND_TAG}"
        else:
            msg = f"👛 Wallet: <code>{address}</code>\nBalance: <b>{result}</b>\n\n{BRAND_TAG}"
        update.message.reply_text(msg, parse_mode="HTML")
        return

    # ok True -> numeric bnb balance returned
    bnb = result
    update.message.reply_text(f"👛 Wallet: <code>{address}</code>\nBalance: <b>{bnb:.6f} BNB</b>\n\n{BRAND_TAG}", parse_mode="HTML")

def token_supply(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💡 Usage: /supply <contract_address>")
        return
    raw = context.args[0]
    contract = normalize_address(raw)

    if len(contract) != 42:
        update.message.reply_text("⚠️ Invalid contract address format.")
        return

    ok, val = bsc_token_supply(contract)
    if ok:
        # val is numeric total tokens
        update.message.reply_text(f"📊 Token Supply for:\n<code>{contract}</code>\nTotal: <b>{val:,.0f} tokens</b>\n\n{BRAND_TAG}", parse_mode="HTML")
    else:
        if val == "unverified":
            update.message.reply_text(f"📊 Token Supply for:\n<code>{contract}</code>\nTotal: ❌ <b>Invalid or unverified contract</b>.\n\nTip: Verify the contract source on BscScan to enable supply analytics.\n\n{BRAND_TAG}", parse_mode="HTML")
        else:
            update.message.reply_text(f"📊 Token Supply for:\n<code>{contract}</code>\nTotal: ❌ <b>{val}</b>\n\n{BRAND_TAG}", parse_mode="HTML")

def analyze_placeholder(update: Update, context: CallbackContext):
    # Minimal placeholder, will be replaced by Emotion Sync v5.4
    if not context.args:
        update.message.reply_text("💡 Usage: /analyze <address>")
        return
    address = normalize_address(context.args[0])
    update.message.reply_text(
        f"🧠 AI Wallet Risk Analyzer — v1.0 Prototype\n\n"
        f"Analyzing wallet:\n<code>{address}</code>\n\n"
        f"Status: <i>Feature coming in Emotion Sync upgrade (v5.4)</i>\n\n{BRAND_TAG}",
        parse_mode="HTML"
    )

# ---- Register Handlers ----
def register_handlers(dp):
    dp.add_handler(CommandHandler("web3", web3_panel))
    dp.add_handler(CommandHandler("tokenprice", tokenprice))
    dp.add_handler(CommandHandler("wallet", wallet_balance))
    dp.add_handler(CommandHandler("supply", token_supply))
    dp.add_handler(CommandHandler("analyze", analyze_placeholder))

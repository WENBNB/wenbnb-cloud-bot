# plugins/airdrop_check.py
"""
Airdrop eligibility checker
Version: 2.5 (Locked & Approved)
Mode: Hybrid — works with /airdropcheck <wallet> or detects if wallet address is typed.
"""

import re, requests, html
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

BSCSCAN_API = "https://api.bscscan.com/api"
BSCSCAN_KEY = os.getenv("BSCSCAN_API_KEY", "")
WENBNB_CONTRACT = "0x0000000000000000000000000000000000000000"  # <-- your token contract here

wallet_regex = re.compile(r"0x[a-fA-F0-9]{40}")

def register_handlers(dp):
    dp.add_handler(CommandHandler("airdropcheck", airdrop_check, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, passive_check))

def check_balance(address: str):
    """Query BscScan for WENBNB token balance."""
    try:
        params = {
            "module": "account",
            "action": "tokenbalance",
            "contractaddress": WENBNB_CONTRACT,
            "address": address,
            "tag": "latest",
            "apikey": BSCSCAN_KEY
        }
        r = requests.get(BSCSCAN_API, params=params, timeout=10)
        j = r.json()
        if j.get("status") == "1":
            raw_bal = int(j["result"])
            return raw_bal / 1e18
        return None
    except Exception:
        return None

def format_reply(address, balance):
    lines = []
    lines.append(f"🎁 <b>Airdrop Eligibility Check</b>")
    lines.append(f"🔗 <b>Wallet:</b> <code>{address[:10]}...{address[-6:]}</code>")
    if balance is not None and balance > 0:
        lines.append(f"✅ <b>Eligible!</b> You hold {balance:,.4f} WENBNB.")
        lines.append("Keep your wallet connected to claim updates.")
    else:
        lines.append(f"⚠️ <b>Not Eligible.</b> No WENBNB tokens found.")
        lines.append("You can still participate in community tasks!")
    lines.append("")
    lines.append(BRAND_FOOTER)
    return "\n".join(lines)

def airdrop_check(update: Update, context: CallbackContext):
    """Command version"""
    args = context.args
    if not args:
        update.message.reply_text("Usage: /airdropcheck <wallet-address>\nExample:\n/airdropcheck 0xabc123...")
        return
    address = args[0].strip()
    if not wallet_regex.match(address):
        update.message.reply_text("❌ Invalid address format.")
        return
    update.message.reply_text(f"🔍 Checking eligibility for {address[:10]}...")
    balance = check_balance(address)
    update.message.reply_text(format_reply(address, balance), parse_mode="HTML")

def passive_check(update: Update, context: CallbackContext):
    """Smart passive detection when user types a wallet address directly"""
    msg = update.message.text.strip()
    match = wallet_regex.search(msg)
    if not match:
        return
    address = match.group(0)
    update.message.reply_text(f"🧠 Detected wallet address: {address[:10]}...\nChecking eligibility...")
    balance = check_balance(address)
    update.message.reply_text(format_reply(address, balance), parse_mode="HTML")

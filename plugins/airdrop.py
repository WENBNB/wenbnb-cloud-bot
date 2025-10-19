from telegram.ext import CommandHandler
import requests
def register(dispatcher, core):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
def airdrop_cmd(update, context):
    if not context.args:
        update.message.reply_text("Usage: /airdropcheck 0xYourWallet")
        return
    addr = context.args[0]
    token = core.get("WEN_TOKEN_ADDRESS")
    api = core.get("BSCSCAN_API_KEY")
    if not token or token.startswith("0x0000"):
        update.message.reply_text("Airdrop not configured.")
        return
    try:
        url = f"https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={token}&address={addr}&tag=latest&apikey={api}"
        r = requests.get(url).json()
        bal = int(r.get("result", "0"))
        if bal > 0:
            update.message.reply_text(f"âœ… {addr} holds tokens (balance: {bal}). Eligible.")
        else:
            update.message.reply_text("âŒ Not eligible (balance 0).")
    except:
        update.message.reply_text("Airdrop check failed.")

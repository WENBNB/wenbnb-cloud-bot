from telegram.ext import CommandHandler
import requests
def register(dispatcher, core):
    dispatcher.add_handler(CommandHandler("tokeninfo", tokeninfo_cmd))
def tokeninfo_cmd(update, context):
    token = core.get("WEN_TOKEN_ADDRESS")
    api = core.get("BSCSCAN_API_KEY")
    if not token or token.startswith("0x0000"):
        update.message.reply_text("Token not configured yet.")
        return
    try:
        url = f"https://api.bscscan.com/api?module=stats&action=tokensupply&contractaddress={token}&apikey={api}"
        r = requests.get(url).json()
        supply = r.get("result", "N/A")
        update.message.reply_text(f"Token supply: {supply}")
    except:
        update.message.reply_text("Token info fetch failed.")

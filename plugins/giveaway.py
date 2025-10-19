from telegram.ext import CommandHandler
import time, random
def register(dispatcher, core):
    dispatcher.add_handler(CommandHandler("giveaway_start", giveaway_start))
    dispatcher.add_handler(CommandHandler("giveaway_end", giveaway_end))
def giveaway_start(update, context):
    uid = update.effective_user.id
    owner = core.get("OWNER_ID")
    if uid != int(owner):
        update.message.reply_text("Admin only.")
        return
    update.message.reply_text("ðŸŽ‰ Giveaway started! Reply to this message to enter.")
def giveaway_end(update, context):
    uid = update.effective_user.id
    owner = core.get("OWNER_ID")
    if uid != int(owner):
        update.message.reply_text("Admin only.")
        return
    update.message.reply_text("ðŸ† Giveaway ended â€” winner logic coming soon!")

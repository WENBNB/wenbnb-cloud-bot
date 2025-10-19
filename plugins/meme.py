from telegram.ext import CommandHandler
def register(dispatcher, core):
    dispatcher.add_handler(CommandHandler("meme", meme_cmd))
def meme_cmd(update, context):
    topic = " ".join(context.args) or "WENBNB moon"
    update.message.reply_text(f"When {topic} pumps, I buy memes not stocks. ðŸš€")

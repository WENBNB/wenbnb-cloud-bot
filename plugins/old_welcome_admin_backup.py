from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext

def register(dispatcher, core):
    # 🟢 Register command handlers
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_new_member))
    dispatcher.add_handler(CommandHandler("adminsay", admin_say))

# 🔹 Auto-welcome message
def welcome_new_member(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        update.message.reply_text(
            f"👋 Welcome {member.first_name} to *WENBNB Community*! 🚀\n"
            "Type /menu to explore bot features.",
            parse_mode="Markdown"
        )

# 🔸 Admin-only message broadcast
def admin_say(update: Update, context: CallbackContext):
    owner_id = int(core.get("OWNER_ID", "0")) if core else 0
    user_id = update.effective_user.id

    if user_id != owner_id:
        update.message.reply_text("⛔ Only admin can use this command.")
        return

    text = " ".join(context.args)
    if not text:
        update.message.reply_text("Usage: /adminsay <message>")
        return

    update.message.reply_text(f"📢 Admin Announcement:\n{text}")

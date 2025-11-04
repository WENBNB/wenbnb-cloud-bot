import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from threading import Timer
import time

PENDING_VERIFY = {}  # user_id: time stamp
VERIFY_TIMEOUT = 60  # seconds
ADMIN_IDS = [int(os.getenv("OWNER_ID", "0"))]

def send_welcome(update, context, member):
    chat_id = update.effective_chat.id
    uid = member.id
    name = member.first_name

    PENDING_VERIFY[uid] = time.time()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Verify", callback_data=f"verify_{uid}")]
    ])

    msg = (
        f"⚡ Welcome {name}!\n\n"
        f"To verify you're human, reply with 👋 or tap the button below.\n"
        f"⏳ You have **{VERIFY_TIMEOUT}s**.\n\n"
        f"🤖 Anti-bot shield active"
    )

    context.bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="Markdown")
    Timer(VERIFY_TIMEOUT, check_kick, args=(context, chat_id, uid, name)).start()


def check_kick(context, chat_id, uid, name):
    if uid in PENDING_VERIFY:
        try:
            # context.bot.kick_chat_member(chat_id, uid)  # uncomment to kick
            context.bot.send_message(
                chat_id,
                f"❌ {name} did not verify.\n"
                f"Fake vibes = No entry 🚫"
            )
        except:
            pass
        PENDING_VERIFY.pop(uid, None)


def welcome_new_member(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        if member.id in ADMIN_IDS:
            continue
        send_welcome(update, context, member)


def verify_response(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if uid not in PENDING_VERIFY:
        return

    if "👋" in text or text.lower() in ["hi", "hello", "yo", "hey"]:
        PENDING_VERIFY.pop(uid, None)
        context.bot.send_message(chat_id, "✅ Verified! Welcome aboard 🚀")
        return

    return


def button_verify(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = update.effective_user.id
    data = query.data

    if data == f"verify_{uid}" and uid in PENDING_VERIFY:
        PENDING_VERIFY.pop(uid, None)
        query.answer("Verified ✅")
        query.edit_message_text("✅ Verified! Welcome aboard 🚀")
    else:
        query.answer("Not for you ⚠️")


def register_handlers(dp, config=None):
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_new_member), group=3)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, verify_response), group=3)
    dp.add_handler(CallbackQueryHandler(button_verify, pattern="verify_"))

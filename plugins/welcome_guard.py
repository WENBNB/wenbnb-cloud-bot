import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
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

    # 🚫 Restrict new user from sending anything until verified
    context.bot.restrict_chat_member(
        chat_id,
        uid,
        permissions=ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Verify", callback_data=f"verify_{uid}")]
    ])

    msg = (
        f"⚡ Welcome {name}!\n\n"
        f"Tap ✅ Verify below to prove you're human.\n"
        f"⏳ {VERIFY_TIMEOUT}s to verify.\n\n"
        f"🤖 Anti-bot shield active"
    )

    context.bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="Markdown")
    Timer(VERIFY_TIMEOUT, check_kick, args=(context, chat_id, uid, name)).start()


def check_kick(context, chat_id, uid, name):
    if uid in PENDING_VERIFY:
        try:
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


# ✅ No typing allowed anyway, but still ignore text if pending
def verify_response(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    if uid not in PENDING_VERIFY:
        return
    # silently ignore until button press
    return


def button_verify(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = update.effective_user.id
    data = query.data

    if data == f"verify_{uid}" and uid in PENDING_VERIFY:
        PENDING_VERIFY.pop(uid, None)

        # ✅ Unrestrict user after verify
        context.bot.restrict_chat_member(
            query.message.chat.id,
            uid,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )

        query.answer("Verified ✅")
        query.edit_message_text("✅ Verified! Welcome aboard 🚀")
    else:
        query.answer("Not for you ⚠️")


def register_handlers(dp, config=None):
    dp.add_handler(
        MessageHandler(Filters.status_update.new_chat_members, welcome_new_member),
        group=2
    )

    dp.add_handler(
        MessageHandler(Filters.text & ~Filters.command, verify_response),
        group=2
    )

    dp.add_handler(CallbackQueryHandler(button_verify, pattern="verify_"))

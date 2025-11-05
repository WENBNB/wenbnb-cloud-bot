import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from telegram.ext import MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from threading import Timer
import time
import secrets

PENDING_VERIFY = {}  # uid: {"ts": time, "msg_id": id, "token": token}
VERIFY_TIMEOUT = 60  # seconds
ADMIN_IDS = [int(os.getenv("OWNER_ID", "0"))]


def send_welcome(update, context, member):
    chat_id = update.effective_chat.id
    uid = member.id
    name = member.first_name or "User"

    token = secrets.token_urlsafe(6)  # unique button token

    # store pending info
    PENDING_VERIFY[uid] = {
        "ts": time.time(),
        "chat_id": chat_id,
        "token": token,
        "msg_id": None
    }

    # Restrict new user
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
        [InlineKeyboardButton("✅ Verify", callback_data=f"verify_{uid}_{token}")]
    ])

    msg = (
        f"⚡ Welcome {name}!\n\n"
        f"Tap ✅ Verify below to prove you're human.\n"
        f"⏳ {VERIFY_TIMEOUT}s to verify.\n\n"
        f"🤖 Anti-bot shield active"
    )

    sent = context.bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="Markdown")
    PENDING_VERIFY[uid]["msg_id"] = sent.message_id

    Timer(VERIFY_TIMEOUT, check_kick, args=(context, chat_id, uid, name)).start()


def check_kick(context, chat_id, uid, name):
    if uid not in PENDING_VERIFY:
        return

    try:
        context.bot.send_message(chat_id, f"❌ {name} did not verify.\nFake vibes = No entry 🚫")
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
    if uid in PENDING_VERIFY:
        try:
            update.message.delete()  # delete unverified messages
        except:
            pass
        return


def button_verify(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = update.effective_user.id
    data = query.data.split("_")

    if len(data) != 3:
        query.answer("Invalid ⚠️")
        return

    action, target_uid, token = data

    try:
        target_uid = int(target_uid)
    except:
        query.answer("Invalid ⚠️")
        return

    if uid != target_uid:
        query.answer("This isn't your verify button ❌", show_alert=True)
        return

    if uid not in PENDING_VERIFY:
        query.answer("Expired ❌", show_alert=True)
        return

    if PENDING_VERIFY[uid]["token"] != token:
        query.answer("Invalid token ❌", show_alert=True)
        return

    chat_id = PENDING_VERIFY[uid]["chat_id"]
    msg_id = PENDING_VERIFY[uid]["msg_id"]

    # verified, remove pending
    PENDING_VERIFY.pop(uid, None)

    # unrestrict user
    context.bot.restrict_chat_member(
        chat_id,
        uid,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    # delete verify button message
    try:
        context.bot.delete_message(chat_id, msg_id)
    except:
        pass

    query.answer("Verified ✅")
    context.bot.send_message(chat_id, f"✅ Verified! **Welcome to WENBNB 🧠⚡️**", parse_mode="Markdown")


def register_handlers(dp, config=None):
    dp.add_handler(
        MessageHandler(Filters.text & ~Filters.command, verify_response),
        group=0
    )

    dp.add_handler(
        MessageHandler(Filters.status_update.new_chat_members, welcome_new_member),
        group=1
    )

    dp.add_handler(
        CallbackQueryHandler(button_verify, pattern="^verify_"),
        group=2
    )

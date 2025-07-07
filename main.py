import os
import json
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")  # Put your bot token here in .env file
ADMIN_CHAT_ID = 7671281090      # Your Telegram user ID to receive admin messages
REFERRAL_FILE = "referrals.json"
referrals = {}

def load_referrals():
    global referrals
    if os.path.exists(REFERRAL_FILE):
        with open(REFERRAL_FILE, "r") as f:
            referrals = json.load(f)

def save_referrals():
    with open(REFERRAL_FILE, "w") as f:
        json.dump(referrals, f)

def is_valid_bsc_address(address):
    # Simple regex to validate BSC address format
    return re.match(r"^0x[a-fA-F0-9]{40}$", address) is not None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)
    args = context.args
    referrer_id = None

    if args:
        try:
            ref_code = args[0]
            referrer_id = ref_code.replace("ref", "")
            if referrer_id == user_id:
                referrer_id = None
        except:
            referrer_id = None

    if referrer_id and user_id not in referrals:
        referrals[user_id] = referrer_id
        save_referrals()
        username = f"@{user.username}" if user.username else "No username"
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"User {user.full_name} ({username}), ID: {user_id}, was referred by user ID: {referrer_id}",
        )

    chat_id = update.effective_chat.id

    caption_start = (
        "🎉 Earn Rewards with HESCO Tokens! 🎉\n\n"
        "Start your journey now! Register and get $5 worth of HESCO tokens as a welcome gift, plus up to $2 for each referral!\n\n"
        "HESCO Token is developed by Black Stone Construction to revolutionize the construction industry using blockchain technology."
    )
    if os.path.exists("start.jpg"):
        with open("start.jpg", "rb") as photo1:
            await context.bot.send_photo(chat_id=chat_id, photo=photo1, caption=caption_start)

    caption_info = (
        "📩 Add HESCO Token to your wallet and send your receiving address to qualify for your reward.\n\n"
        "🪙 Name: HESCO Token\n💠 Symbol: HESCO\n🔗 Network: BNB Smart Chain (BSC)\n"
        "🧾 Contract: `0xb5e9541143c137b19286990223c0a140137c5f18`"
    )
    if os.path.exists("info.jpg"):
        with open("info.jpg", "rb") as photo2:
            await context.bot.send_photo(chat_id=chat_id, photo=photo2, caption=caption_info, parse_mode="Markdown")

    # Contract button removed as requested

    instruction = (
        "🛠️ How to add HESCO token to your wallet:\n\n"
        "🪙 Token Name: HESCO Token\n💠 Symbol: HESCO\n🔗 Network: BNB Smart Chain (BEP20)\n"
        "🧾 Contract: `0xb5e9541143c137b19286990223c0a140137c5f18`"
    )
    await context.bot.send_message(chat_id=chat_id, text=instruction, parse_mode="Markdown")

    keyboard = [
        [
            InlineKeyboardButton("Info", callback_data="info"),
            InlineKeyboardButton("🎁 Claim Reward", callback_data="get_reward"),
            InlineKeyboardButton("🔗 Refer Friends", callback_data="refer"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text="🔽 Please choose an option:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "info":
        caption = (
            "📩 Add HESCO Token to your wallet and send your receiving address to claim your reward.\n\n"
            "🪙 Name: HESCO Token\n💠 Symbol: HESCO\n🔗 Network: BNB Smart Chain (BSC)\n"
            "🧾 Contract: `0xb5e9541143c137b19286990223c0a140137c5f18`"
        )
        if os.path.exists("info.jpg"):
            with open("info.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="Markdown")

    elif query.data == "get_reward":
        reward_message = (
            "🎁 Please first add the HESCO token to your wallet:\n\n"
            "🪙 Token Name: HESCO Token\n"
            "💠 Symbol: HESCO\n"
            "🔗 Network: BNB Smart Chain (BEP20)\n"
            "📜 Contract Address:\n"
            "`0xb5e9541143c137b19286990223c0a140137c5f18`\n\n"
            "🔹 *Now please send your HESCO wallet address to receive your tokens.*"
        )
        await context.bot.send_message(chat_id=chat_id, text=reward_message, parse_mode="Markdown")

    elif query.data == "refer":
        user_id = str(query.from_user.id)
        bot_username = (await context.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start=ref{user_id}"

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📢 Your personal referral link to share with friends:\n\n"
                f"{invite_link}\n\n"
                f"Earn up to $10 HESCO for each successful referral!"
            ),
        )


async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)
    address = update.message.text.strip()

    if not is_valid_bsc_address(address):
        await update.message.reply_text(
            "❌ Invalid address! The BSC address should start with `0x` and be 42 characters long."
        )
        return

    await update.message.reply_text("✅ Thank you! Your wallet address has been received.")

    username = f"@{user.username}" if user.username else "No username"
    referrer_id = referrals.get(user_id, "No referrer")
    admin_text = (
        f"💼 New wallet address received:\n"
        f"👤 User: {user.full_name} ({username})\n"
        f"🆔 User ID: {user_id}\n"
        f"🏦 Address: {address}\n"
        f"🔗 Referrer ID: {referrer_id}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)


async def myrefs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    count = sum(1 for uid in referrals if referrals[uid] == user_id)
    await update.message.reply_text(f"👥 You have referred {count} user(s) so far.")


def main():
    load_referrals()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myrefs", myrefs))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), receive_address))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

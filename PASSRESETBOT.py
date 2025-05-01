import logging
import random
import requests
import string
import uuid
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = '7734188960:AAGObwsdTNUtocyHzxLLwjHYVDI1QtbY4xU'

logging.basicConfig(level=logging.INFO)

# Counters
total_requests = 0
success_count = 0
fail_count = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"**Hey {update.effective_user.first_name or 'there'}!**\n\n"
        "Welcome to the **Insta Reset Bot**.\n"
        "Use `/help` to see all commands.",
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Available Commands:**\n\n"
        "`/reset username` - Send IG reset link\n"
        "`/check username` - Check if IG account exists\n"
        "`/stats` - Show reset stats\n"
        "`/about` - Bot & creator info",
        parse_mode=ParseMode.MARKDOWN
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Bot Name:** Insta Reset Bot\n"
        "**Created by:** Haiwan\n"
        "Power: Python + Telegram Bot API",
        parse_mode=ParseMode.MARKDOWN
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 **Bot Stats:**\n\n"
        f"Total Resets: `{total_requests}`\n"
        f"Success: `{success_count}`\n"
        f"Failed: `{fail_count}`",
        parse_mode=ParseMode.MARKDOWN
    )

def send_reset_request(user_input):
    headers = {
        'User-Agent': f"Instagram 123.0.0.21.114 Android ({random.randint(10, 12)}; 320dpi; 720x1280; samsung; SM-G532F; grandpplte; mt6737m; en_US)",
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Language': 'en-US',
    }

    payload = {
        '_csrftoken': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        'guid': str(uuid.uuid4()),
        'device_id': str(uuid.uuid4()),
    }

    if '@' in user_input and not user_input.startswith('@'):
        payload['user_email'] = user_input
    else:
        payload['username'] = user_input.replace("@", "")

    response = requests.post(
        "https://i.instagram.com/api/v1/accounts/send_password_reset/",
        headers=headers,
        data=payload
    )

    return response.json()

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_requests, success_count, fail_count

    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Usage:\n`/reset username` or `/reset email@example.com`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    user_input = context.args[0]
    total_requests += 1
    await update.message.reply_text("⏳ Sending reset request...")

    try:
        response = send_reset_request(user_input)
        if "obfuscated_email" in response:
            success_count += 1
            await update.message.reply_text(
                f"✅ Reset link sent to `{user_input}`",
                parse_mode=ParseMode.MARKDOWN
            )
        elif "message" in response:
            fail_count += 1
            await update.message.reply_text(f"❌ {response['message']}")
        else:
            fail_count += 1
            await update.message.reply_text("❌ Invalid account. Try again.")
    except Exception as e:
        fail_count += 1
        await update.message.reply_text(f"⚠️ Error:\n`{str(e)}`", parse_mode=ParseMode.MARKDOWN)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: `/check username`", parse_mode=ParseMode.MARKDOWN)
        return

    username = context.args[0].replace("@", "")
    url = f"https://www.instagram.com/{username}/?__a=1&__d=1"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        await update.message.reply_text(f"✅ **@{username}** exists on Instagram!", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"❌ **@{username}** doesn't exist.", parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("check", check))

    print("Bot is running...")
    app.run_polling()
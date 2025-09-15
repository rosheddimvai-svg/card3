from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# === Bot Token এবং চ্যানেল আইডি ===
TOKEN = "7845699149:AAEEKpzHFt5gd6LbApfXSsE8de64f8IaGx0"

PENDING_CHANNEL = -1003036699455
APPROVED_CHANNEL = -1002944346537
BROADCAST_CHANNEL = -1003018121134

# ইউজারদের লিস্ট (broadcast এর জন্য)
user_list = set()


# === Start Menu ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_list.add(user.id)  # প্রতিটা ইউজার সেভ হবে
    keyboard = [
        [InlineKeyboardButton("🪙 Card Sell", callback_data="card_sell")],
        [InlineKeyboardButton("💼 Wallet Setup / Rules", callback_data="wallet_rules")],
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/YourAdminUsername")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "স্বাগতম! নিচ থেকে একটি অপশন সিলেক্ট করুন 👇", reply_markup=reply_markup
    )


# === Callback Menu ===
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "card_sell":
        await query.message.reply_text("অনুগ্রহ করে আপনার কার্ড ডিটেলস পাঠান।")
    elif query.data == "wallet_rules":
        await query.message.reply_text(
            "💼 Wallet Setup / Rules:

আপনার ওয়ালেট ঠিকানা সঠিকভাবে পাঠাবেন।
❌ ভুল তথ্য দিলে কার্ড রিজেক্ট হবে।"
        )


# === Card Submission ===
async def forward_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_list.add(user.id)  # ইউজার লিস্টে অ্যাড

    text = f"""
📩 নতুন কার্ড সাবমিশন:
👤 নাম: {user.first_name}
🔗 Username: @{user.username}
🆔 User ID: {user.id}

💳 Card: {update.message.text}
"""
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{user.id}")],
        [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(PENDING_CHANNEL, text, reply_markup=reply_markup)


# === Confirm / Reject ===
async def card_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, user_id = query.data.split("_")
    user_id = int(user_id)

    if action == "confirm":
        await context.bot.send_message(APPROVED_CHANNEL, f"✅ User {user_id} এর কার্ড অনুমোদিত হয়েছে।")
        await context.bot.send_message(user_id, "🎉 আপনার কার্ড অনুমোদিত হয়েছে ✅")
    elif action == "reject":
        await context.bot.send_message(user_id, "❌ দুঃখিত, আপনার কার্ড রিজেক্ট করা হয়েছে।")

    await query.answer()


# === Broadcast Command ===
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != BROADCAST_CHANNEL:
        await update.message.reply_text("⚠️ এই কমান্ড শুধু Broadcast চ্যানেলে ব্যবহার করা যাবে।")
        return

    if not context.args:
        await update.message.reply_text("ব্যবহার করুন: /broadcast আপনার_মেসেজ")
        return

    message = " ".join(context.args)

    for uid in user_list:
        try:
            await context.bot.send_message(uid, f"📢 Broadcast:
{message}")
        except:
            pass  # যাদের মেসেজ পাঠানো যাবে না তাদের স্কিপ

    await update.message.reply_text("✅ Broadcast পাঠানো হয়েছে।")


# === Main ===
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_menu, pattern="^(card_sell|wallet_rules)$"))
    app.add_handler(CallbackQueryHandler(card_action, pattern="^(confirm|reject)_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_card))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

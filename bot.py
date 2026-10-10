import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

# لیست کشورهای پشتیبانی‌شده توسط randomuser.me
COUNTRIES = {
    "🇺🇸 US": "us", "🇬🇧 GB": "gb", "🇫🇷 FR": "fr", "🇩🇪 DE": "de",
    "🇮🇷 IR": "ir", "🇹🇷 TR": "tr", "🇮🇳 IN": "in", "🇧🇷 BR": "br",
    "🇦🇺 AU": "au", "🇨🇦 CA": "ca", "🇪🇸 ES": "es", "🇮🇹 IT": "it",
    "🇳🇱 NL": "nl", "🇩🇰 DK": "dk", "🇫🇮 FI": "fi", "🇮🇪 IE": "ie",
    "🇲🇽 MX": "mx", "🇳🇿 NZ": "nz", "🇳🇴 NO": "no", "🇷🇸 RS": "rs",
    "🇨🇭 CH": "ch", "🇺🇦 UA": "ua",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ارسال پیام خوش‌آمدگویی با دکمه‌ها."""
    keyboard = [
        [InlineKeyboardButton("🎲 کاربر تصادفی (بدون فیلتر)", callback_data="random")],
        [InlineKeyboardButton("🌍 انتخاب کشور", callback_data="choose_country")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! 👋\n\nمن ربات تولید کاربر تصادفی هستم.\n"
        "می‌تونی یک کاربر کاملاً تصادفی بگیری یا کشور مورد نظرت رو انتخاب کنی.",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت دکمه‌های فشرده شده."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "random":
        await generate_user(query, context, None)
    elif data == "choose_country":
        # ساخت دکمه‌های انتخاب کشور (۲ ستونه)
        keyboard = []
        items = list(COUNTRIES.items())
        for i in range(0, len(items), 2):
            row = []
            row.append(InlineKeyboardButton(items[i][0], callback_data=f"gen_{items[i][1]}"))
            if i + 1 < len(items):
                row.append(InlineKeyboardButton(items[i+1][0], callback_data=f"gen_{items[i+1][1]}"))
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🌍 کدوم کشور؟", reply_markup=reply_markup)
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🎲 کاربر تصادفی (بدون فیلتر)", callback_data="random")],
            [InlineKeyboardButton("🌍 انتخاب کشور", callback_data="choose_country")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "سلام! 👋\n\nمن ربات تولید کاربر تصادفی هستم.\n"
            "می‌تونی یک کاربر کاملاً تصادفی بگیری یا کشور مورد نظرت رو انتخاب کنی.",
            reply_markup=reply_markup
        )
    elif data.startswith("gen_"):
        nationality = data.replace("gen_", "")
        await generate_user(query, context, nationality)

async def generate_user(query, context, nationality=None) -> None:
    """تولید اطلاعات کاربر تصادفی از API."""
    url = "https://randomuser.me/api/"
    if nationality:
        url += f"?nat={nationality}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        user = response.json()["results"][0]

        name = f"{user['name']['title']} {user['name']['first']} {user['name']['last']}"
        gender = "🤵" if user['gender'] == "male" else "👩"
        location = user['location']
        city = location['city']
        country = location['country']
        email = user['email']
        phone = user['phone']
        dob = user['dob']['date'][:10]
        picture = user['picture']['large']

        text = (
            f"👤 *نام:* {name} {gender}\n"
            f"📍 *شهر:* {city}\n"
            f"🌍 *کشور:* {country}\n"
            f"📧 *ایمیل:* {email}\n"
            f"📞 *تلفن:* {phone}\n"
            f"🎂 *تاریخ تولد:* {dob}"
        )

        keyboard = [
            [InlineKeyboardButton("🔄 یکی دیگه", callback_data=f"gen_{nationality or 'random'}")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # اگر query از نوع CallbackQuery است، edit می‌کنیم
        if hasattr(query, 'edit_message_media'):
            # چون عکس داریم، از edit_message_media استفاده می‌کنیم
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    except Exception as e:
        error_msg = f"❌ خطا در دریافت اطلاعات: {str(e)}"
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(error_msg, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "دستورات:\n"
        "/start - شروع مجدد\n"
        "/help - راهنما\n\n"
        "یا از دکمه‌های داخل پیام استفاده کن."
    )

def main() -> None:
    if not TOKEN:
        print("❌ متغیر BOT_TOKEN تنظیم نشده است!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("✅ ربات در حال اجراست...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

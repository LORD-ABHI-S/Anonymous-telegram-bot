from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes


# ==================================================
# 🔐 YOUR BOT TOKEN
# ==================================================

BOT_TOKEN = "8903984207:AAEP3i937FTzULEa7VB5p-eif3_wLPcdSeQ"


# ==================================================
# 📢 YOUR CHANNELS
# ==================================================

CHANNELS = [
    ("🗽 𝐌ᴀɪɴ 𝐂ʜᴀɴɴᴇʟ", "https://t.me/AS_WORKSPACE"),
    ("⛩️ 𝐀ɴɪᴍᴇ", "https://t.me/ASAR_ANIME"),
    ("🕹️ 𝐀ɴɪᴍᴇ 𝐔ᴘᴅᴀᴛᴇ", "https://t.me/ASAR_UPDATES"),
    ("🗿 𝐎ᴡɴᴇʀ 𝐂ʜᴀɴɴᴇʟ", "https://t.me/DENZI_BOY"),
    ("🚩 𝐇ɪɴᴅᴜ 𝐏ᴀʀɪꜱʜᴀᴅ", "https://t.me/+yM8ib1pIgvdlNDRl"),
]


# ==================================================
# 👥 YOUR GROUPS
# ==================================================

GROUPS = [
    ("🧩 𝐀𝐒 𝐂ᴏᴍᴍᴜɴɪᴛʏ", "https://t.me/AS_COMUNITY"),
    ("🪎 𝐀ꜱᴀʀ 𝐀ɴɪᴍᴇ 𝐆ʀᴏᴜᴘ", "https://t.me/ASAR_ANIME_GROUP"),
    ("🥐 𝐋ɪᴛᴛʟᴇ 𝐂ᴏʀɴᴇʀ", "https://t.me/+WxEX51XqDPI2OTc1"),
    ("🌪️ 𝐂ʏᴄʟᴏɴᴇ 𝐋ᴏᴠᴇ 𝐆ᴄ", "https://t.me/CYCLONE_LOVE"),
    ("🕉️ 𝐇ɪɴᴅᴜ 𝐏ᴀʀɪꜱʜᴀᴅ 𝐆ᴄ", "https://t.me/+_d5V-BNjD7w3NDA1"),
]


# ==================================================
# 🏠 HOME MENU
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton(
            "📢 𝐂ʜᴀɴɴᴇʟꜱ",
            callback_data="channels"
        )],

        [InlineKeyboardButton(
            "👥 𝐆ʀᴏᴜᴘꜱ",
            callback_data="groups"
        )],

        [InlineKeyboardButton(
            "⚠️ 𝐑ᴇᴘᴏʀᴛ 𝐏ʀᴏʙʟᴇᴍ",
            url="https://t.me/ASAR_OWNER_BOT"
        )],
    ]

    await update.message.reply_text(
        "𓆩 ᴀꜱ ᴡᴏʀᴋꜱᴘᴀᴄᴇ 𓆪\n\n"
        "ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ᴡᴏʀᴋꜱᴘᴀᴄᴇ\n"
        "ᴄʜᴏᴏꜱᴇ ᴀ ꜱᴇᴄᴛɪᴏɴ ʙᴇʟᴏᴡ 👇",

        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================================================
# 🔘 BUTTON HANDLER
# ==================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    # ==================================================
    # 📢 CHANNELS
    # ==================================================

    if query.data == "channels":

        keyboard = []

        for name, link in CHANNELS:

            keyboard.append([
                InlineKeyboardButton(
                    name,
                    url=link
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "🔙 𝐁ᴀᴄᴋ",
                callback_data="home"
            )
        ])

        await query.edit_message_text(
            "📢 𝐂ʜᴀɴɴᴇʟꜱ\n\n"
            "ᴄʜᴏᴏꜱᴇ ᴀ ᴄʜᴀɴɴᴇʟ ʙᴇʟᴏᴡ 👇",

            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    # ==================================================
    # 👥 GROUPS
    # ==================================================

    elif query.data == "groups":

        keyboard = []

        for name, link in GROUPS:

            keyboard.append([
                InlineKeyboardButton(
                    name,
                    url=link
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "🔙 𝐁ᴀᴄᴋ",
                callback_data="home"
            )
        ])

        await query.edit_message_text(
            "👥 𝐆ʀᴏᴜᴘꜱ\n\n"
            "ᴄʜᴏᴏꜱᴇ ᴀ ɢʀᴏᴜᴘ ʙᴇʟᴏᴡ 👇",

            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    # ==================================================
    # 🏠 BACK TO HOME
    # ==================================================

    elif query.data == "home":

        keyboard = [
            [InlineKeyboardButton(
                "📢 𝐂ʜᴀɴɴᴇʟꜱ",
                callback_data="channels"
            )],

            [InlineKeyboardButton(
                "👥 𝐆ʀᴏᴜᴘꜱ",
                callback_data="groups"
            )],

            [InlineKeyboardButton(
                "⚠️ 𝐑ᴇᴘᴏʀᴛ 𝐏ʀᴏʙʟᴇᴍ",
                url="https://t.me/ASAR_OWNER_BOT"
            )],
        ]

        await query.edit_message_text(
            "𓆩 ᴀꜱ ᴡᴏʀᴋꜱᴘᴀᴄᴇ 𓆪\n\n"
            "ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ᴡᴏʀᴋꜱᴘᴀᴄᴇ\n"
            "ᴄʜᴏᴏꜱᴇ ᴀ ꜱᴇᴄᴛɪᴏɴ ʙᴇʟᴏᴡ 👇",

            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ==================================================
# 🚀 START BOT
# ==================================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("🤖 AS WORKSPACE BOT IS RUNNING...")

    app.run_polling()


# ==================================================
# ▶ RUN
# ==================================================

if __name__ == "__main__":
    main()

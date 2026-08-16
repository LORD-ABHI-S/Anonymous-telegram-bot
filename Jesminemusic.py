# ============================================================
#              JASMINE X MUSIC — TELEGRAM BOT
# ============================================================

import asyncio
import os
import sqlite3
import time
import random

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

from pytgcalls import PyTgCalls
from yt_dlp import YoutubeDL


# ============================================================
#                     BASIC CONFIG
# ============================================================

API_ID = 30672609

# PUT YOUR NEW API HASH HERE
API_HASH = "7b1d2b631725691a89df22a377f3c53a"

# PUT YOUR NEW BOT TOKEN HERE
BOT_TOKEN = "8835783533:AAGnnXZXxACuN9s6Pgj-Ku16drdoPOI3mm4"

# PUT YOUR NEW USER SESSION STRING HERE
SESSION_STRING = "1BVtsOJ8Bu3_uu1j7BKSQQKEwlxZTDKoeiPafFWpSLteCvqem886-IwLU_CzEEvpZiovba5LtFQC_wIN9JWqDa2iiXfys35n3HbTowfqL5J3qJoARvo1ODvPes0whQCuqV0l6s--_y6WnO35L12fe4IXJBY70IYhTejshOUxF_D01ylgvGxAAQICJQHVOIySV12Reu-_PFdIBMi_sDfUqlKbUdQA7xD5k6yYoL7XOjr7-YgWrlXNSGzSDpxWxK0cc5B2wOPGrmrYyMMhN4vtOX_k4pqDalRk7eiKtn8Vx67-Ukx5ffQcz7gTPvf8NE2U6erK1fpnEdabpCOJ7NJ5PVPFReiblE18="


# ============================================================
#                     BOT INFORMATION
# ============================================================

BOT_NAME = "JASMINE X MUSIC"
BOT_USERNAME = "JasmineXmusicbot"

OWNER_ID = 7499742938

# Initial bot admin
INITIAL_ADMINS = {
    6239941845,
}


# ============================================================
#                     SUPPORT / CHANNELS
# ============================================================

SUPPORT_GROUP = "https://t.me/+rSUEvBcRswkwYThh"
SUPPORT_GROUP_ID = -1004462544512

SUPPORT_CHANNEL = "https://t.me/AS_WORKSPACE"
SUPPORT_CHANNEL_ID = -1003598183958

# UPDATED LINK
UPDATE_CHANNEL = "https://t.me/Jasminesupport"
UPDATE_CHANNEL_ID = -1004402662430


# ============================================================
#                    WELCOME / START SETTINGS
# ============================================================

# ============================================================
# CHANGE YOUR START PHOTO HERE
# ============================================================
#
# Put the Telegram PHOTO FILE_ID here.
#
# Example:
#
# START_PHOTO = "AgACAgUAAxkBAAIB..."
#
# Leave empty if you don't want a photo.
#

START_PHOTO = ""


# ============================================================
# CHANGE YOUR START MESSAGE HERE
# ============================================================

START_MESSAGE = """
🎵 **JASMINE X MUSIC**

Welcome to JASMINE X MUSIC.

🎧 Music • 🎬 Video • ⚡ Fast Playback

Play music and videos in your Telegram
voice chats with a simple command.

Use /help to see all commands.
"""


# ============================================================
#                         DATABASE
# ============================================================

DB_NAME = "jasmine_music.db"

db = sqlite3.connect(
    DB_NAME,
    check_same_thread=False
)

db.row_factory = sqlite3.Row

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    added_at INTEGER
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    added_at INTEGER
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    added_by INTEGER,
    added_at INTEGER
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    name TEXT PRIMARY KEY,
    value TEXT
)
""")


db.commit()


# ============================================================
#                      DATABASE FUNCTIONS
# ============================================================

def save_user(user):

    if not user:
        return

    cursor.execute(
        """
        INSERT OR REPLACE INTO users
        (user_id, first_name, username, added_at)
        VALUES (?, ?, ?, COALESCE(
            (SELECT added_at FROM users WHERE user_id=?),
            ?
        ))
        """,
        (
            user.id,
            user.first_name or "",
            user.username or "",
            user.id,
            int(time.time())
        )
    )

    db.commit()


def save_group(chat):

    if not chat:
        return

    cursor.execute(
        """
        INSERT OR REPLACE INTO groups
        (chat_id, title, added_at)
        VALUES (?, ?, COALESCE(
            (SELECT added_at FROM groups WHERE chat_id=?),
            ?
        ))
        """,
        (
            chat.id,
            chat.title or "",
            chat.id,
            int(time.time())
        )
    )

    db.commit()


def add_admin(user_id, added_by):

    cursor.execute(
        """
        INSERT OR REPLACE INTO admins
        (user_id, added_by, added_at)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            added_by,
            int(time.time())
        )
    )

    db.commit()


def remove_admin(user_id):

    cursor.execute(
        "DELETE FROM admins WHERE user_id=?",
        (user_id,)
    )

    db.commit()


def is_bot_admin(user_id):

    if user_id == OWNER_ID:
        return True

    cursor.execute(
        "SELECT user_id FROM admins WHERE user_id=?",
        (user_id,)
    )

    return cursor.fetchone() is not None


def get_admins():

    cursor.execute(
        "SELECT user_id FROM admins ORDER BY added_at"
    )

    return [
        row["user_id"]
        for row in cursor.fetchall()
    ]


# ============================================================
#                    INITIAL ADMIN SETUP
# ============================================================

for admin_id in INITIAL_ADMINS:

    add_admin(
        admin_id,
        OWNER_ID
    )


# ============================================================
#                        CLIENTS
# ============================================================

bot = Client(
    "jasmine_x_music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


user = Client(
    "jasmine_x_music_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


calls = PyTgCalls(user)


# ============================================================
#                         QUEUES
# ============================================================

queues = {}


# ============================================================
#                      YOUTUBE SEARCH
# ============================================================

def search_youtube(query, video=False):

    if video:

        format_string = (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
            "best[ext=mp4]/best"
        )

    else:

        format_string = (
            "bestaudio[ext=m4a]/"
            "bestaudio/best"
        )

    options = {
        "format": format_string,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "noplaylist": True,
        "nocheckcertificate": True,
    }

    with YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            query,
            download=False
        )

        if "entries" in info:

            entries = info.get("entries")

            if not entries:
                raise Exception(
                    "No result found."
                )

            info = entries[0]

        return {
            "title": info.get(
                "title",
                "Unknown"
            ),
            "url": info.get("url"),
            "webpage": info.get(
                "webpage_url",
                ""
            ),
            "type": "video" if video else "audio"
        }


# ============================================================
#                       ADMIN CHECK
# ============================================================

async def group_admin_required(message):

    if not message.from_user:
        return False

    if is_bot_admin(
        message.from_user.id
    ):
        return True

    try:

        member = await bot.get_chat_member(
            message.chat.id,
            message.from_user.id
        )

        return member.status in (
            "administrator",
            "owner"
        )

    except Exception:

        return False


# ============================================================
#                      START BUTTONS
# ============================================================

async def start_keyboard():

    me = await bot.get_me()

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎵 Commands",
                    callback_data="commands"
                ),
                InlineKeyboardButton(
                    "➕ Add Me",
                    url=(
                        f"https://t.me/{me.username}"
                        "?startgroup=true"
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Updates",
                    url=UPDATE_CHANNEL
                ),
                InlineKeyboardButton(
                    "💬 Support",
                    url=SUPPORT_GROUP
                )
            ]
        ]
    )


# ============================================================
#                   SAVE USERS / GROUPS
# ============================================================

@bot.on_message(filters.incoming)
async def database_handler(_, message: Message):

    try:

        if message.from_user:

            save_user(
                message.from_user
            )

        if message.chat.type in (
            ChatType.GROUP,
            ChatType.SUPERGROUP
        ):

            save_group(
                message.chat
            )

    except Exception:
        pass


# ============================================================
#                         /START
# ============================================================

@bot.on_message(filters.command("start"))
async def start_command(_, message: Message):

    if message.from_user:

        save_user(
            message.from_user
        )

    keyboard = await start_keyboard()

    if START_PHOTO:

        await message.reply_photo(
            START_PHOTO,
            caption=START_MESSAGE,
            reply_markup=keyboard
        )

    else:

        await message.reply_text(
            START_MESSAGE,
            reply_markup=keyboard
        )


# ============================================================
#                         /HELP
# ============================================================

@bot.on_message(filters.command("help"))
async def help_command(_, message: Message):

    await message.reply_text(
        """
🎵 **JASMINE X MUSIC**

🎧 **Music**
/play <song>
/skip
/pause
/resume
/stop
/queue
/song
/shuffle
/clear

🎬 **Video**
/vplay <video>

👑 **Admin**
/panel
/stats
/ping
/addadmin
/deladmin
/admins
/broadcast
/broadcast_groups
/setstart
/resetstart
/restart
"""
    )


# ============================================================
#                   COMMANDS BUTTON
# ============================================================

@bot.on_callback_query(
    filters.regex("^commands$")
)
async def commands_button(_, query: CallbackQuery):

    await query.answer()

    await query.message.edit_text(
        """
🎵 **JASMINE X MUSIC**

▶️ `/play song`
🎬 `/vplay video`
⏭ `/skip`
⏸ `/pause`
▶️ `/resume`
⏹ `/stop`
📜 `/queue`
🎵 `/song`
🔀 `/shuffle`
🗑 `/clear`

Use /help for the complete command list.
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="back_start"
                    )
                ]
            ]
        )
    )


@bot.on_callback_query(
    filters.regex("^back_start$")
)
async def back_start(_, query: CallbackQuery):

    await query.answer()

    keyboard = await start_keyboard()

    await query.message.delete()

    if START_PHOTO:

        await bot.send_photo(
            query.message.chat.id,
            START_PHOTO,
            caption=START_MESSAGE,
            reply_markup=keyboard
        )

    else:

        await bot.send_message(
            query.message.chat.id,
            START_MESSAGE,
            reply_markup=keyboard
        )


# ============================================================
#                          /PLAY
# ============================================================

@bot.on_message(filters.command("play"))
async def play_command(_, message: Message):

    if message.chat.type not in (
        ChatType.GROUP,
        ChatType.SUPERGROUP
    ):

        await message.reply_text(
            "❌ Use /play inside a group."
        )

        return

    if len(message.command) < 2:

        await message.reply_text(
            "🎵 Usage:\n"
            "`/play song name`"
        )

        return

    query = " ".join(
        message.command[1:]
    )

    chat_id = message.chat.id

    status = await message.reply_text(
        "🔎 **Searching...**"
    )

    try:

        song = await asyncio.to_thread(
            search_youtube,
            query,
            False
        )

    except Exception as e:

        await status.edit_text(
            "❌ Search failed.\n\n"
            f"`{str(e)[:500]}`"
        )

        return

    if chat_id not in queues:

        queues[chat_id] = []

    queues[chat_id].append(
        song
    )

    position = len(
        queues[chat_id]
    )

    if position > 1:

        await status.edit_text(
            f"✅ **Added to queue**\n\n"
            f"🎵 {song['title']}\n"
            f"📍 Position: `{position}`"
        )

        return

    try:

        await calls.play(
            chat_id,
            song["url"]
        )

        await status.edit_text(
            f"🎵 **Now Playing**\n\n"
            f"**{song['title']}**"
        )

    except Exception as e:

        queues.pop(
            chat_id,
            None
        )

        await status.edit_text(
            "❌ Could not start playback.\n\n"
            f"`{str(e)[:500]}`"
        )


# ============================================================
#                         /VPLAY
# ============================================================

@bot.on_message(filters.command("vplay"))
async def vplay_command(_, message: Message):

    if message.chat.type not in (
        ChatType.GROUP,
        ChatType.SUPERGROUP
    ):

        await message.reply_text(
            "❌ Use /vplay inside a group."
        )

        return

    if len(message.command) < 2:

        await message.reply_text(
            "🎬 Usage:\n"
            "`/vplay video name`"
        )

        return

    query = " ".join(
        message.command[1:]
    )

    chat_id = message.chat.id

    status = await message.reply_text(
        "🎬 **Searching video...**"
    )

    try:

        video = await asyncio.to_thread(
            search_youtube,
            query,
            True
        )

    except Exception as e:

        await status.edit_text(
            "❌ Video search failed.\n\n"
            f"`{str(e)[:500]}`"
        )

        return

    if chat_id not in queues:

        queues[chat_id] = []

    queues[chat_id].append(
        video
    )

    position = len(
        queues[chat_id]
    )

    if position > 1:

        await status.edit_text(
            f"🎬 **Video added to queue**\n\n"
            f"🎥 {video['title']}\n"
            f"📍 Position: `{position}`"
        )

        return

    try:

        await calls.play(
            chat_id,
            video["url"]
        )

        await status.edit_text(
            f"🎬 **Now Playing Video**\n\n"
            f"**{video['title']}**"
        )

    except Exception as e:

        queues.pop(
            chat_id,
            None
        )

        await status.edit_text(
            "❌ Could not start video playback.\n\n"
            f"`{str(e)[:500]}`"
        )


# ============================================================
#                         /SKIP
# ============================================================

@bot.on_message(filters.command("skip"))
async def skip_command(_, message: Message):

    if not await group_admin_required(
        message
    ):

        await message.reply_text(
            "❌ Admin only."
        )

        return

    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:

        await message.reply_text(
            "📭 Queue is empty."
        )

        return

    queues[chat_id].pop(0)

    if not queues[chat_id]:

        try:

            await calls.leave_call(
                chat_id
            )

        except Exception:
            pass

        await message.reply_text(
            "⏹ **Queue finished.**"
        )

        return

    next_song = queues[chat_id][0]

    try:

        await calls.play(
            chat_id,
            next_song["url"]
        )

        icon = (
            "🎬"
            if next_song["type"] == "video"
            else "🎵"
        )

        await message.reply_text(
            f"{icon} **Now Playing**\n\n"
            f"**{next_song['title']}**"
        )

    except Exception as e:

        await message.reply_text(
            f"❌ Playback error:\n"
            f"`{str(e)[:500]}`"
        )


# ============================================================
#                         /PAUSE
# ============================================================

@bot.on_message(filters.command("pause"))
async def pause_command(_, message: Message):

    if not await group_admin_required(
        message
    ):

        await message.reply_text(
            "❌ Admin only."
        )

        return

    try:

        await calls.pause(
            message.chat.id
        )

        await message.reply_text(
            "⏸ **Paused.**"
        )

    except Exception as e:

        await message.reply_text(
            f"❌ `{str(e)[:500]}`"
        )


# ============================================================
#                         /RESUME
# ============================================================

@bot.on_message(filters.command("resume"))
async def resume_command(_, message: Message):

    if not await group_admin_required(
        message
    ):

        await message.reply_text(
            "❌ Admin only."
        )

        return

    try:

        await calls.resume(
            message.chat.id
        )

        await message.reply_text(
            "▶️ **Resumed.**"
        )

    except Exception as e:

        await message.reply_text(
            f"❌ `{str(e)[:500]}`"
        )


# ============================================================
#                          /STOP
# ============================================================

@bot.on_message(filters.command("stop"))
async def stop_command(_, message: Message):

    if not await group_admin_required(
        message
    ):

        await message.reply_text(
            "❌ Admin only."
        )

        return

    chat_id = message.chat.id

    queues.pop(
        chat_id,
        None
    )

    try:

        await calls.leave_call(
            chat_id
        )

    except Exception:
        pass

    await message.reply_text(
        "⏹ **Playback stopped.**"
    )


# ============================================================
#                         /QUEUE
# ============================================================

@bot.on_message(filters.command("queue"))
async def queue_command(_, message: Message):

    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:

        await message.reply_text(
            "📭 **Queue is empty.**"
        )

        return

    text = "📜 **JASMINE X MUSIC QUEUE**\n\n"

    for index, song in enumerate(
        queues[chat_id],
        1
    ):

        icon = (
            "🎬"
            if song["type"] == "video"
            else "🎵"
        )

        text += (
    f"`{index}.` {icon} "
    f"{song['title']}\n"
        )
